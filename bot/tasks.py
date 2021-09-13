from datetime import datetime
from hashlib import sha256
import json
from typing import Any

from celery import task
import redis
import telegram
from telegram import InlineKeyboardButton
import yaml

from bot.handlers.boardroom_api_client import BroadroomAPIClient
from bot.handlers.bot import Bot
from bot.handlers.button_handlers import DASH_LINE, TgView
from bot.handlers.utils import TgUrl
from conf.settings import REDIS_URL, TELEGRAM_TOKEN
from .models import BotChatUser, Proposal, Subscription

# Connect to our Redis instance.
redis_instance = redis.StrictRedis.from_url(url=REDIS_URL, db=2)

# Reminder periods for active proposals.
remind_periods = [
    3 * 24 * 60 * 60,  # 3 days
    1 * 24 * 60 * 60,  # 1 days
    5 * 60 * 60,  # 5 hour
    1 * 60 * 60,  # 1 hour
    10 * 60,  # 10 min
]

remind_periods_names = ["3 days", "1 days", "5 hour", "1 hour", "10 minutes"]


def hash_dict(d: dict):
    return sha256(json.dumps(d, sort_keys=True).encode("utf8")).hexdigest()


@task(ignore_result=True)
def notify_subscriptions():
    api_client = BroadroomAPIClient()
    bot = Bot(telegram.Bot(TELEGRAM_TOKEN))

    ref_ids = (
        Subscription.objects.all().values("ref_id").distinct().values_list("ref_id", flat=True)
    )
    for ref_id in ref_ids:
        # Fetch the proposal or skip.
        try:
            res = api_client.get_single_proposal(ref_id)
            if "data" not in res:
                raise Exception()
        except Exception:
            continue

        res = res["data"]
        proposal = Proposal()
        proposal.ref_id = res["refId"]
        proposal.title = res["title"]
        proposal.results = res["results"]
        proposal.protocol = res["protocol"]
        proposal.current_state = res["currentState"]
        proposal.total_votes = res["totalVotes"]
        proposal.next_reminder = 0
        try:
            proposal_old = Proposal.objects.get(ref_id=res["refId"])
            proposal_fields = [
                f.name for f in Proposal._meta.get_fields()
            ]  # gives me the list of all the model fields defined in it
            print(proposal_fields)
            diff = list(
                filter(
                    lambda field: getattr(proposal, field, None)
                    != getattr(proposal_old, field, None)
                    and field != "next_reminder"
                    and field != "id",
                    proposal_fields,
                )
            )
            diff = {f: [getattr(proposal, f, None), getattr(proposal_old, f, None)] for f in diff}
            print(diff)
            if len(diff) != 0:
                chat_ids = Subscription.objects.filter(ref_id=ref_id).values_list(
                    "user__user_id", flat=True
                )
                bot.send_bulk(
                    ProposalUpdateTgView(chat_ids, proposal, diff), TgUrl("proposalupdate", {})
                )

                # Update old proposal
                proposal_old.title = proposal.title
                proposal_old.results = proposal.results
                proposal_old.protocol = proposal.protocol
                proposal_old.current_state = proposal.current_state
                proposal_old.total_votes = proposal.total_votes
                proposal_old.save()

            proposal = proposal_old

        except Proposal.DoesNotExist:
            proposal.save()

        end_ts = datetime.fromtimestamp(res["endTimestamp"])
        seconds_delta = int((end_ts - datetime.utcnow()).total_seconds())
        if seconds_delta > remind_periods[proposal.next_reminder]:
            return
        i = proposal.next_reminder
        while seconds_delta <= remind_periods[i]:
            i += 1
        proposal.next_reminder = i
        proposal.save()
        chat_ids = BotChatUser.objects.filter(alerting=True).values_list("user_id", flat=True)
        bot.send_bulk(
            ProposalPeriodtgView(chat_ids, proposal, proposal.next_reminder),
            TgUrl("proposalperiod", {}),
        )

        # Delete proposals if state != active|queued
        if proposal.current_state not in ["active", "queued"]:
            Subscription.objects.filter(ref_id=ref_id).delete()
            Proposal.objects.filter(ref_id=ref_id).delete()


class ProposalUpdateTgView(TgView):
    def __init__(self, chat_ids: list, proposal: Proposal, diff: list) -> None:
        self.proposal = proposal
        self.diff = diff
        super().__init__(chat_ids)

    def render(self, url: TgUrl, data: Any):
        self.msg = f"⚠⚠⚠ *Proposal updated* ⚠⚠⚠\n{DASH_LINE}\n\n"
        self.msg += f"{self._to_message()} \n"
        # We want to subscribe on live proposals.
        if self.proposal.current_state in ["active", "queued"]:
            if Subscription.objects.filter(user__user_id=self.chat_id).exists():
                self.keyboards += [
                    [
                        InlineKeyboardButton(
                            "Unsubscribe",
                            callback_data=TgUrl(
                                "unsubscribe", {"refId": self.proposal.ref_id}
                            ).get(),
                        )
                    ],
                ]
            else:
                self.keyboards += [
                    [
                        InlineKeyboardButton(
                            "Subscribe",
                            callback_data=TgUrl(
                                "subscribe", {"refId": self.proposal.ref_id}
                            ).get(),
                        )
                    ],
                ]
        return super().render(url, data)

    def _to_message(self):
        msg = f"title: *{self.field_state('title')}*\n"
        msg += f"protocol: *{self.field_state('protocol')}*\n"
        msg += f"current state: *{self.field_state('current_state')}*\n"
        msg += f"total votes: *{self.field_state('total_votes')}*\n"
        msg += f"results: \n{yaml.dump(self.field_state('results'))}\n"
        msg += f"next reminder: *{remind_periods_names[self.proposal.next_reminder]}* before the end date."

        return msg

    def field_state(self, field):
        if field in self.diff:
            change_tuple = self.diff[field]
            return f"changed from {change_tuple[0]} to {change_tuple[1]}"
        return getattr(self.proposal, field, None)


class ProposalPeriodtgView(TgView):
    def __init__(self, chat_ids: list, proposal: Proposal, next_reminder: int) -> None:
        self.proposal = proposal
        self.next_reminder = next_reminder
        super().__init__(chat_ids)

    def render(self, url: TgUrl, data: Any):
        self.msg = f"⚠⚠⚠ *Proposal period alert* ⚠⚠⚠\n{DASH_LINE}\n\n"
        self.msg += f"{self._to_message()} \n"
        # We want to subscribe on live proposals.
        if self.proposal.current_state in ["active", "queued"]:
            if Subscription.objects.filter(user__user_id=self.chat_id).exists():
                self.keyboards += [
                    [
                        InlineKeyboardButton(
                            "Unsubscribe",
                            callback_data=TgUrl(
                                "unsubscribe", {"refId": self.proposal.ref_id}
                            ).get(),
                        )
                    ],
                ]
            else:
                self.keyboards += [
                    [
                        InlineKeyboardButton(
                            "Subscribe",
                            callback_data=TgUrl(
                                "subscribe", {"refId": self.proposal.ref_id}
                            ).get(),
                        )
                    ],
                ]
        return super().render(url, data)

    def _to_message(self):
        msg = f"⚠ Proposal voting will ended in *{remind_periods_names[max(self.proposal.next_reminder-1,0)]}*.\n"
        msg += f"title: *{self.proposal.title}*\n"
        msg += f"protocol: *{self.proposal.protocol}*\n"
        msg += f"current state: *{self.proposal.current_state}*\n"
        msg += f"total votes: *{self.proposal.total_votes}*\n"
        msg += f"results: \n{yaml.dump(self.proposal.results)}\n"
        msg += f"next reminder: *{remind_periods_names[self.proposal.next_reminder]}* before the end date."
        return msg
