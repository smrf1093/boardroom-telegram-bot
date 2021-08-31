from .api_handler import BroadroomAPIHandler
from abc import ABC
from bothandler.models import Proposal

class Command(ABC):
    def __init__(self, chat_ids: list) -> None:
        self.msg = ''
        self.api_handler = BroadroomAPIHandler()
        self.chat_id = None
        if len(chat_ids) > 0:
            self.chat_id = chat_ids[0]        
        self.chat_ids = chat_ids

    def execute(self, **kwargs):
        return self.msg
    
    def convert_dict_to_text_v2(self, dictionary, keyIndex=0, spaces=0):
        text = ''
        if keyIndex >= len(dictionary.keys()):
                return text
        currentKey = list(dictionary.keys())[keyIndex]
        if type(dictionary[currentKey]) == dict:
            text += f"{' ' * spaces}{currentKey}: \n"
            text += self.convert_dict_to_text_v2(dictionary[currentKey], keyIndex=0, spaces=spaces+3)
        elif type(dictionary[currentKey]) == list:
            text += f"{' ' * spaces}{currentKey}: \n"
            for value in dictionary[currentKey]:
                if type(value) == dict:
                    text += self.convert_dict_to_text_v2(value, keyIndex=0, spaces=spaces+3)
                else:
                    text += f"  {value} \n"
        else:
            text += f"{' ' * spaces}{currentKey}: {dictionary[currentKey]} \n"
        return text + self.convert_dict_to_text_v2(dictionary, keyIndex+1)
    

class HelpCommand(Command):
    def execute(self, **kwargs):
        self.msg += "Currently the bot supports the following commands: \n"
        self.msg += "/protocols  list of all protocols \n"
        self.msg += "/pdetail<cname>  get single protocol info \n"
        self.msg += "/proposals  list of all proposals \n"
        self.msg += "/refid<id>  get details of a proposal \n"
        self.msg += "/protocolproposals<cname>  get proposals for a protocol  \n"
        self.msg += "/proposalsvotes<id>  get votes for a proposals   \n"
        return super().execute(**kwargs)


class StartCommand(Command):
    IDENTIFIER  = 'start'

    def execute(self, **kwargs):
        return 'Welcome to BroadRoom API telegram bot'

class ProtocolsCommand(Command):
    IDENTIFIER = "protocols"

    bot_command = 'protocols'
    api_address = 'protocols'

    def execute(self, **kwargs):
        json_response = self.api_handler.get_protocols()
        
        if 'data' in json_response:
            for protocol in json_response['data']:
                self.msg += f"{protocol['name']} - /pdetail{protocol['cname']} \n"
            self.msg += "Use the names to access a Single protocol info"
        else:
            self.msg = 'Some error happend from api side'
        return super().execute(**kwargs) 


class ProtocolDetailCommand(Command):  

    IN_IDENTIFIER = "pdetail"

    def execute(self, **kwargs):
        json_response = self.api_handler.get_single_protocol(kwargs['cname'])
        if 'data' in json_response:
            currentProtocol = json_response['data']
            self.msg = self.convert_dict_to_text_v2(currentProtocol)
        else:
            self.msg = 'Some error happend from api side'
        return super().execute(**kwargs)


class ProposalsJsonCommand(Command):
    """
        this will return proposal objects for search or caching 
    """
    def execute(self, **kwargs):
        self.msg = self.api_handler.get_proposals()['data']
        return super().execute(**kwargs)
    
    

class ProposalsCommand(Command):

    IDENTIFIER = "proposals"

    def execute(self, **kwargs):
        json_response = self.api_handler.get_proposals()
        
        if 'data' in json_response:
            proposals = json_response['data']
            counter = 0
            for proposal in proposals:
                counter += 1
                self.msg += f"{self.convert_dict_to_text_v2(proposal)} \n"
                self.msg += f"Available Commands: \n"
                self.msg += f"Details: /refId{proposal['id']} \n"
                self.msg += f"Votes: /proposalvotes{proposal['id']} \n"
                Proposal.objects.get_or_create(p_id=proposal['id'].lower(), ref_id=proposal['refId'])
                
            self.msg += "Use /refId<id> to access a specific proposal information"
            
        else: 
            self.msg = 'Oops there is a problem'
        return super().execute(**kwargs)


class ProtocolProposalsCommand(Command):

    IN_IDENTIFIER = "protocolproposals"

    def execute(self, **kwargs):
        json_response = self.api_handler.get_protocol_proposals(kwargs['cname'])
        if 'data' in json_response:
            for proposal in json_response['data']:
                self.msg += f"{self.convert_dict_to_text_v2(proposal)} \n"
        else:
            self.msg = 'Oops there is a problem'
        return super().execute(**kwargs)


class ProposalDetailCommand(Command):

    IN_IDENTIFIER = 'refid'

    def execute(self, **kwargs):
        json_response = self.api_handler.get_single_proposal(kwargs['refId'])
        if 'data' in json_response:
            self.msg += f"{self.convert_dict_to_text_v2(json_response['data'])} \n"
        else:
            self.msg = 'Oops there is a problem'
        return super().execute(**kwargs)


class ProposalVotesCommand(Command):

    # should take an Id
    IN_IDENTIFIER = 'proposalvotes'

    def execute(self, **kwargs):
        json_response = self.api_handler.get_proposal_votes(kwargs['refId'])
        if 'data' in json_response:
            for vote in json_response['data']:
                self.msg += f"{self.convert_dict_to_text_v2(vote)} \n"
        else:
            self.msg = 'Oops there is a problem'
        return super().execute(**kwargs)


class VotersByAddressCommand(Command):
    def execute(self, **kwargs):
        json_response = self.api_handler.get_votes_by_voters(kwargs['address'])
        if 'data' in json_response:
            for voter in json_response['data']:
                self.msg += f"{self.convert_dict_to_text_v2(voter)} \n"
        else:
            self.msg = 'Oops there is a problem'
        return super().execute(**kwargs)


class ProtocolVotersCommand(Command):

    IN_IDENTIFIER = ''

    def execute(self, **kwargs):
        json_response = self.api_handler.get_protocol_voters(kwargs['cname'])
        if 'data' in json_response:
            for voter in json_response['data']:
                self.msg += f"{self.convert_dict_to_text_v2(voter)} \n"
        else:
            self.msg = 'Oops there is a problem'
        return super().execute(**kwargs)


class VotersCommad(Command):
    def execute(self, **kwargs):
        json_response = self.api_handler.get_voters()
        if 'data' in json_response:
            for voter in json_response['data']:
                self.msg += f"{self.convert_dict_to_text_v2(voter)} \n"
        else:
            self.msg = 'Oops there is a problem'
        return super().execute(**kwargs)

class VoterDetailCommand(Command):
    def execute(self, **kwargs):
        json_response = self.api_handler.get_single_voter(kwargs['address'])
        if 'data' in json_response:
            voter = json_response['data']
            self.msg += f"{self.convert_dict_to_text_v2(voter)} \n"
        else:
            self.msg = 'Oops there is a problem'
        return super().execute(**kwargs)

class StatCommand(Command):
    def execute(self, **kwargs):
        json_response = self.api_handler.get_stat()
        if 'data' in json_response:
            stats = json_response['data']
            self.msg += f"{self.convert_dict_to_text_v2(stats)} \n"
        else:
            self.msg = 'Oops there is a problem'
        return super().execute(**kwargs)


class MessageCommand(Command):
    def execute(self, **kwargs):
        self.msg = kwargs['message']
        return super().execute(**kwargs)
