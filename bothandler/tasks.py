
from celery import task
from .models import VotersVoteSubscribe, ProposalVoteSibscribe
from .bot.bot import Bot
from .bot.bot_commands import VotersByAddressCommand, ProposalVotesCommand

@task(name='notify_subscribers')  
def notify_subsrcibers():
     bot = Bot()
     votes_by_address_subscribers = VotersVoteSubscribe.objects.all()
     votes_by_address_dict = dict()
     for votes_by_address_subscriber in votes_by_address_subscribers:
          if votes_by_address_subscriber.address in votes_by_address_dict:
               votes_by_address_dict[votes_by_address_subscriber.address].append(votes_by_address_subscriber.user)
          else:
               votes_by_address_dict[votes_by_address_subscriber.address] = [votes_by_address_subscriber.user, ]

     for key in votes_by_address_dict.keys():
          bot.bulk_command_executor(VotersByAddressCommand(chat_ids=votes_by_address_dict[key]), address=key)

     
     proposal_votes_subescribers = ProposalVoteSibscribe.objects.all()
     votes_for_proposal_dict = dict()
     for proposal_votes_subescriber in proposal_votes_subescribers:
          if proposal_votes_subescriber.ref_id in votes_for_proposal_dict:
               votes_for_proposal_dict[proposal_votes_subescriber.ref_id].append(proposal_votes_subescriber.user)
          else:
               votes_for_proposal_dict[proposal_votes_subescriber.ref_id] = [proposal_votes_subescriber.user, ]
     
     for key in votes_for_proposal_dict.keys():
          bot.bulk_command_executor(ProposalVotesCommand(chat_ids=votes_for_proposal_dict[key]), refId=key)

