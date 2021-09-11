
from datetime import datetime
from bot.handlers.button_handlers import Button, DASH_LINE
import telegram
from requests import api
from bot.handlers.boardroom_api_client import BroadroomAPIClient
from celery import task
from bot.handlers.bot import Bot
from .models import BotChatUser, Proposal, Subscription
import redis
import yaml
import json
from hashlib import sha256
from bot.handlers.utils import proposal_refid_truncated
from conf.settings import REDIS_URL, TELEGRAM_TOKEN
from telegram import InlineKeyboardButton

# Connect to our Redis instance.
redis_instance = redis.StrictRedis.from_url(url=REDIS_URL, db=2)

# Reminder periods for active proposals.
remind_periods = [
     3 * 24 * 60 * 60, # 3 days
     1 * 24 * 60 * 60, # 1 days
     5 * 60 * 60, # 5 hour
     1 * 60 * 60, # 1 hour
     10 * 60, # 10 min
]

remind_periods_names = [
     "3 days",
     "1 days",
     "5 hour",
     "1 hour",
     "10 minutes"
]

def hash_dict(d: dict):
     return sha256(json.dumps(d,sort_keys=True).encode('utf8')).hexdigest()

@task(ignore_result=True)
def notify_subscriptions():
     api_client = BroadroomAPIClient()
     bot = Bot(telegram.Bot(TELEGRAM_TOKEN))
     
     ref_ids = Subscription.objects.all().values("ref_id").distinct().values_list("ref_id", flat=True)
     for ref_id in ref_ids:
          res = api_client.get_single_proposal(ref_id)
          proposal = Proposal()
          proposal.ref_id = res["refId"]
          proposal.title = res["title"]
          proposal.results = res["results"]
          proposal.protocol = res["protocol"]
          proposal.current_state = res["currentState"]
          proposal.total_votes = res["totoalVotes"]
          proposal.next_reminder = remind_periods[0]
          try:
               proposal_old = Proposal.objects.get(ref_id=res["refId"])
               proposal_fields = Proposal._meta.get_all_field_names() # gives me the list of all the model fields defined in it
               diff = filter(lambda field: getattr(proposal,field,None)!=getattr(proposal_old,field,None) and field != "next_reminder", proposal_fields)
               if len(diff) != 0:
                    chat_ids = Subscription.objects.filter(ref_id=ref_id).values_list("user__user_id", flat=True)
                    bot.send_bulk(ProposalUpdateButton(chat_ids, proposal, diff))
               
                    # Update old proposal
                    proposal_old.title = proposal.title
                    proposal_old.results = proposal.results
                    proposal_old.protocol = proposal.protocol
                    proposal_old.current_state = proposal.current_state
                    proposal_old.total_votes = proposal.total_votes
                    proposal_old.next_reminder = proposal.next_reminder
                    proposal_old.save()
                    proposal = proposal_old

          except Proposal.DoesNotExist:
               proposal.save()
          
          end_ts = datetime.fromtimestamp(res["endTimestamp"])
          seconds_delta = (end_ts - datetime.utcnow()).total_seconds
          if seconds_delta > remind_periods[proposal.next_reminder]:
               return
          i = proposal.next_reminder
          while seconds_delta <= remind_periods[i]:
               i += 1
          proposal.next_reminder = i
          proposal.save()
          chat_ids = BotChatUser.objects.filter(user__alerting=True).values_list("user_id", flat=True)
          bot.send_bulk(ProposalPeriodButton(chat_ids, proposal, proposal.next_reminder))
     




class ProposalUpdateButton(Button):
     def __init__(self, chat_ids: list, proposal: Proposal, diff: list) -> None:
         self.proposal = proposal
         self.diff = diff
         super().__init__(chat_ids)
     
     def render(self, **kwargs):
          self.msg = f"{DASH_LINE}\n⚠⚠⚠ Proposal updated ⚠⚠⚠\n{DASH_LINE}\n\n"
          self.msg += f"{self._to_message()} \n"
          # We want to subscribe on live proposals.
          if self.update['currentState'] in ["active", "queued"]:
               if Subscription.objects.filter(user__user_id=self.chat_id).exists():
                    self.keyboards += [
                    [InlineKeyboardButton("Unsubscribe", callback_data="/unsubscribe"+proposal_refid_truncated(kwargs["refId"]))],
                    ]
               else:
                    self.keyboards += [
                    [InlineKeyboardButton("Subscribe", callback_data="/subscribe"+proposal_refid_truncated(kwargs["refId"]))],
                    ]
          return super().render(**kwargs)

     def _to_message(self):
          msg = f"title: {self.proposal.title}\n"
          msg += f"protocol: {self.proposal.protocol}\n"
          msg += f"current state: {self.proposal.current_state}\n"
          msg += f"total votes: {self.proposal.total_votes}\n"
          msg += f"results: {self.proposal.results}\n"
          msg += f"next reminder: {remind_periods_names[self.proposal.next_reminder]} before the end date."



class ProposalPeriodButton(Button):
     def __init__(self, chat_ids: list, proposal: Proposal, next_reminder: int) -> None:
         self.proposal = proposal
         self.next_reminder = next_reminder
         super().__init__(chat_ids)
     
     def render(self, **kwargs):
          self.msg = f"{DASH_LINE}\n⚠⚠⚠ Proposal period alert ⚠⚠⚠\n{DASH_LINE}\n\n"
          self.msg += f"{self._to_message()} \n"
          # We want to subscribe on live proposals.
          if self.update['currentState'] in ["active", "queued"]:
               if Subscription.objects.filter(user__user_id=self.chat_id).exists():
                    self.keyboards += [
                    [InlineKeyboardButton("Unsubscribe", callback_data="/unsubscribe"+proposal_refid_truncated(kwargs["refId"]))],
                    ]
               else:
                    self.keyboards += [
                    [InlineKeyboardButton("Subscribe", callback_data="/subscribe"+proposal_refid_truncated(kwargs["refId"]))],
                    ]
          return super().render(**kwargs)


     def _to_message(self):
          msg = f"⚠ Proposal voting will ended in {remind_periods_names[max(self.proposal.next_reminder-1,0)]}."
          msg += f"title: {self.proposal.title}\n"
          msg += f"protocol: {self.proposal.protocol}\n"
          msg += f"current state: {self.proposal.current_state}\n"
          msg += f"total votes: {self.proposal.total_votes}\n"
          msg += f"results: {self.proposal.results}\n"
          msg += f"next reminder: {remind_periods_names[self.proposal.next_reminder]} before the end date."
