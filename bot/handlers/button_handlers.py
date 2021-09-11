from bot.handlers.utils import proposal_refid, proposal_refid_truncated
from .boardroom_api_client import BroadroomAPIClient
from abc import ABC
import bot.handlers.static_text
from telegram import ReplyKeyboardMarkup, Update, ReplyKeyboardRemove
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackContext,
)
import redis
import yaml
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from bot.models import  BotChatUser, Subscription


DASH_LINE = "-" * 50
class KeyboardResponse:
    keyboards: list
    message: str

    def __init__(self, message: str, keyboards: list = None) -> None:
        self.message = message
        self.keyboards = keyboards

class Button(ABC):
    def __init__(self, chat_ids: list) -> None:
        self.msg = ''
        self.keyboards = []
        self.api_client = BroadroomAPIClient()
        self.chat_id = None
        if len(chat_ids) > 0:
            self.chat_id = chat_ids[0]        
        self.chat_ids = chat_ids

    def render(self, **kwargs) -> KeyboardResponse:
        # escape invalid telegram chars.
        self.msg = self.msg.replace("_", "\\_") \
                .replace("*", "\\*") \
                .replace("[", "\\[") \
                .replace("`", "\\`")
        return KeyboardResponse(self.msg, self.keyboards)
    
    def to_message(self, dictionary):
        return yaml.dump(dictionary, sort_keys=False)
        

class SubscriptionsButton(Button):
    IDENTIFIER = "subscriptions"

    def render(self, **kwargs):
        subs = Subscription.objects.filter(user__user_id=self.chat_id)
        self.msg = f"Subscription\n{DASH_LINE}\n\n"
        if len(subs)>0:
            for sub in subs:
                self.keyboards.append(
                    [InlineKeyboardButton(sub.proposal_title, callback_data=f"refid{sub.ref_id}")],
                )
        else:
            self.msg = 'No subscriptions found!'
        self.keyboards += [
            [InlineKeyboardButton("Back", callback_data="/start")],
        ]
        return super().render(**kwargs) 

class SubscribeButton(Button):
    IDENTIFIER = "subscribe"

    def render(self, **kwargs):
        json_response = self.api_client.get_single_proposal(kwargs['refId'])
        if "data" in json_response:
            user = BotChatUser.objects.filter(user_id=self.chat_id)
            if len(user) == 1:
                sub, _ = Subscription.objects.get_or_create(user_id=user[0].id, ref_id=kwargs['refId'], proposal_title=json_response['data']['title'])
                self.msg = f"Subscribed to {json_response['data']['title']}"
            else:
                self.msg = 'An error happend'
        else:
            self.msg = 'An error happend'
        self.keyboards += [
            [InlineKeyboardButton("Back", callback_data=f"refid{proposal_refid_truncated(kwargs['refId'])}")],
        ]
        return super().render(**kwargs) 

class UnsubscribeButton(Button):
    IDENTIFIER = "unsubscribe"

    def render(self, **kwargs):
        json_response = self.api_client.get_single_proposal(kwargs['refId'])
        if "data" in json_response:
            Subscription.objects.filter(user__user_id=self.chat_id, ref_id=kwargs['refId']).delete()
            self.msg += f"Unsubscribed from {json_response['data']['title']}"
        else:
            self.msg = 'An error happend'
        self.keyboards += [
            [InlineKeyboardButton("Back", callback_data=f"refid{proposal_refid_truncated(kwargs['refId'])}")],
        ]
        return super().render(**kwargs) 

class ProtocolsButton(Button):
    IDENTIFIER = "protocols"
    api_address = 'protocols'

    def render(self, **kwargs):
        json_response = self.api_client.get_protocols_cached()
        
        self.msg = "Protocols (sorted by name)"
        if 'data' in json_response:
            for protocol in json_response['data']:
                self.keyboards.append(
                    [InlineKeyboardButton(protocol['name'], callback_data="/pdetail"+protocol["cname"])],
                )
        else:
            self.msg = 'Some error happend from api side'
        self.keyboards += [
            [InlineKeyboardButton("Back", callback_data="/start")],
        ]
        return super().render(**kwargs) 

    def to_message(self, dictionary):
        data = {k:v for k,v in dictionary.items() if k not in ["icons", "cname"]}
        yaml_str = yaml.dump(data, sort_keys=False)
        # Adding a large icon to the response
        if "icons" in dictionary:
            yaml_str += "\n" + dictionary["icons"][-1]["url"]
        return yaml_str

class ProtocolDetailButton(Button):  

    IN_IDENTIFIER = "pdetail"

    def render(self, **kwargs):
        json_response = self.api_client.get_single_protocol_cached(kwargs['cname'])
        self.msg = f"Protocol details for: {kwargs['cname']}\n{DASH_LINE}\n\n"
        if 'data' in json_response:
            currentProtocol = json_response['data']
            self.msg += self.to_message(currentProtocol)
        else:
            self.msg = 'Some error happend from api side'
        self.keyboards += [
            [InlineKeyboardButton("Active proposals", callback_data=f"/protocolproposals{kwargs['cname']}_active")],
            [InlineKeyboardButton("Executed proposals", callback_data=f"/protocolproposals{kwargs['cname']}_executed")],
            [InlineKeyboardButton("Canceled proposals", callback_data=f"/protocolproposals{kwargs['cname']}_canceled")],
            [InlineKeyboardButton("Queued proposals", callback_data=f"/protocolproposals{kwargs['cname']}_queued")],
            [InlineKeyboardButton("Voters", callback_data="/protocolvoters"+kwargs['cname'])],
            [InlineKeyboardButton("Back", callback_data="protocols")],
        ]
        return super().render(**kwargs)

    def to_message(self, dictionary):
        if "icons" in dictionary:
            out = {k:v for k,v in dictionary.items() if k not in ["icons"]}
            yaml_str =  yaml.dump(out, sort_keys=False)
            yaml_str += "\n\n" + dictionary["icons"][-1]["url"]
        else:
            yaml_str = yaml.dump(dictionary, sort_keys=False)
        return yaml_str



class ProtocolProposalsButton(Button):

    IN_IDENTIFIER = "protocolproposals"

    def render(self, **kwargs):
        parts = kwargs['cname'].split("_")
        requested_state = parts[1]
        cname = parts[0]
        json_response = self.api_client.get_protocol_proposals_cached(cname)
        self.msg = f"Proposals for {cname} \n"
        if 'data' in json_response:
            for proposal in json_response['data']:
                if proposal["currentState"] == requested_state:
                    self.keyboards.append(
                        [InlineKeyboardButton(proposal["title"], callback_data=f"refid"+proposal_refid_truncated(proposal["refId"]))]
                    )
        else:
            self.msg = 'Oops there is a problem'
        self.keyboards += [
            [InlineKeyboardButton("Back", callback_data="/pdetail"+cname)],
        ]
        return super().render(**kwargs)


class ProposalDetailButton(Button):

    IN_IDENTIFIER = 'refid'

    def render(self, **kwargs):
        json_response = self.api_client.get_single_proposal_cached(kwargs['refId'])
        self.msg = f"Proposal details for:\n{kwargs['refId']}\n{DASH_LINE}\n\n"
        protocol = ""
        current_state = ""
        if 'data' in json_response:
            self.msg += f"{self.to_message(json_response['data'])} \n"
            protocol = json_response["data"]["protocol"]
            current_state = json_response["data"]["currentState"]
        else:
            self.msg = 'Oops there is a problem'
        
        # We want to subscribe on live proposals.
        if current_state in ["active", "queued"]:
            if Subscription.objects.filter(user__user_id=self.chat_id).exists():
                self.keyboards += [
                    [InlineKeyboardButton("Unsubscribe", callback_data="/unsubscribe"+proposal_refid_truncated(kwargs["refId"]))],
                ]
            else:
                self.keyboards += [
                    [InlineKeyboardButton("Subscribe", callback_data="/subscribe"+proposal_refid_truncated(kwargs["refId"]))],
                ]
        self.keyboards += [
            [InlineKeyboardButton("Votes", callback_data="/proposalvotes"+proposal_refid_truncated(kwargs["refId"]))],
            [InlineKeyboardButton("Back", callback_data=f"/protocolproposals{protocol}_{current_state}")],
        ]
        return super().render(**kwargs)

    def to_message(self, dictionary):
        dictionary = {k:v for k,v in dictionary.items() if k in ["title", "protocol", "proposer", "totalVotes", "currentState", "choices", "results"]}
        return yaml.dump(dictionary, sort_keys=False)


class ProposalVotesButton(Button):

    # should take an Id
    IN_IDENTIFIER = 'proposalvotes'

    def render(self, **kwargs):
        json_response = self.api_client.get_proposal_votes_cached(kwargs['refId'])
        self.msg = f"Proposal votes for ref_id:\n{kwargs['refId']} \n\n"
        if 'data' in json_response:
            for vote in json_response['data']:
                self.msg += f"{self.to_message(vote)} \n"
                self.msg += f"{DASH_LINE}\n"
        else:
            self.msg = 'Oops there is a problem'
        self.keyboards += [
            [InlineKeyboardButton("Back", callback_data="refid"+proposal_refid_truncated(kwargs["refId"]))],
        ]
        return super().render(**kwargs)

    def to_message(self, dictionary):
        dictionary = {k:v for k,v in dictionary.items() if k in ["proposalId", "protocol", "power", "choice"]}
        return yaml.dump(dictionary, sort_keys=False)



class VotersByAddressButton(Button):
    """
        The voter address should be included here 
    """
    IN_IDENTIFIER = 'voteraddress'

    def render(self, **kwargs):
        json_response = self.api_client.get_votes_by_voters_cached(kwargs['address'])
        self.msg = f"Voter votes for voter:\n{kwargs['address']} \n\n"
        if 'data' in json_response:
            for voter in json_response['data']:
                self.msg += f"{self.to_message(voter)} \n"
                self.msg += f"{DASH_LINE}\n"

        else:
            self.msg = 'Oops there is a problem'
        self.keyboards += [
            [InlineKeyboardButton("Back", callback_data="votersdetail"+kwargs['address'])],
        ]
        return super().render(**kwargs)

    def to_message(self, dictionary):
        dictionary = {k:v for k,v in dictionary.items() if k in ["proposalId", "protocol", "power", "choice"]}
        return yaml.dump(dictionary, sort_keys=False)

class ProtocolVotersButton(Button):

    IN_IDENTIFIER = 'protocolvoters'

    def render(self, **kwargs):
        json_response = self.api_client.get_protocol_voters_cached(kwargs['cname'])
        self.msg = f"Protocol voters for: {kwargs['cname']}\n{DASH_LINE}\n\n"

        if 'data' in json_response:
            for voter in json_response['data']:
                self.keyboards.append(
                    [InlineKeyboardButton(voter['address'], callback_data=f"/votersdetail{voter['address']}")]
                )
        else:
            self.msg = 'Oops there is a problem'
        self.keyboards += [
            [InlineKeyboardButton("Back", callback_data="protocol"+kwargs['cname'])],
        ]
        return super().render(**kwargs)


class VotersButton(Button):

    IDENTIFIER = 'voters'

    def render(self, **kwargs):
        json_response = self.api_client.get_voters()
        self.msg = f"Voters\n{DASH_LINE}\n\n"
        if 'data' in json_response:
            for voter in json_response['data']:
                self.keyboards.append(
                    [InlineKeyboardButton(voter['address'], callback_data=f"/votersdetail{voter['address']}")]
                )
        else:
            self.msg = 'Oops there is a problem'
        self.keyboards += [
            [InlineKeyboardButton("Back", callback_data="start")],
        ]
        return super().render(**kwargs)

class VoterDetailButton(Button):

    IN_IDENTIFIER = 'votersdetail'

    def render(self, **kwargs):
        json_response = self.api_client.get_single_voter_cached(kwargs['address'])
        self.msg = f"Voter details\n{DASH_LINE}\n\n"
        if 'data' in json_response:
            voter = json_response['data']
            self.msg += f"{self.to_message(voter)} \n"
        else:
            self.msg = 'Oops there is a problem'
        self.keyboards += [
            [InlineKeyboardButton("Votes", callback_data=f"/voteraddress{kwargs['address']}")],
            [InlineKeyboardButton("Back", callback_data="start")],
        ]
        return super().render(**kwargs)


class StatButton(Button):
    def render(self, **kwargs):
        json_response = self.api_client.get_stat()
        if 'data' in json_response:
            stats = json_response['data']
            self.msg += f"{self.to_message(stats)} \n"
        else:
            self.msg = 'Oops there is a problem'
        self.keyboards += [
            [InlineKeyboardButton("Back", callback_data="start")],
        ]
        return super().render(**kwargs)


class MessageButton(Button):
    def render(self, **kwargs):
        self.msg = kwargs['message']
        return super().render(**kwargs)    
