import json
import requests
from django.http import JsonResponse
from bothandler.bot.bot import Bot
from bothandler.bot.bot_commands import (
    HelpCommand,
    StartCommand, 
    ProtocolsCommand,
    ProtocolDetailCommand, 
    ProposalsCommand,
    ProposalDetailCommand,
    ProtocolProposalsCommand,
    MessageCommand,
    ProposalVotesCommand,
    VotersByAddressCommand,
    ProtocolVotersCommand,
    VotersCommand,
    VoterDetailCommand,

)
from bothandler.models import (
    Proposal,
    BotChatUser
)
# Create your views here.
from django.views import View

class BroadroomView(View):

    def post(self, request, *args, **kwargs):
        
        self.t_data = json.loads(request.body)
        # print(request.body)
        if "edited_message" in self.t_data:
            self.t_message = self.t_data["edited_message"]
        else:
            self.t_message = self.t_data["message"]
        self.t_chat = self.t_message["chat"]

        try:
            command = self.t_message["text"].strip().lower()
        except Exception as e:
            return JsonResponse({"ok": "POST request processed"})

        command = command.lstrip("/")
        chat = ""
        if not chat:
            chat = {"chat_id": self.t_chat["id"], "_id": "some id"}
        self.bot = Bot()
        if command == StartCommand.IDENTIFIER:
            # save the user information in database 
            BotChatUser.objects.create(user_bot_id=self.t_chat["id"])
            self.bot.command_executor(command_class=StartCommand(chat_ids=[self.t_chat["id"]]))
        elif command == ProtocolsCommand.IDENTIFIER:
            self.bot.command_executor(command_class=ProtocolsCommand(chat_ids=[self.t_chat["id"]]))
        elif ProtocolDetailCommand.IN_IDENTIFIER in command:
            # remove command identifier
            cname = command.replace(ProtocolDetailCommand.IN_IDENTIFIER, '')
            self.bot.command_executor(command_class=ProtocolDetailCommand(chat_ids=[self.t_chat["id"]]), cname=cname)
        elif command == ProposalsCommand.IDENTIFIER:
            self.bot.command_executor(command_class=ProposalsCommand(chat_ids=[self.t_chat["id"]]))
        elif ProposalDetailCommand.IN_IDENTIFIER in command: 
            # remove the identifier 
            pid = command.replace(ProposalDetailCommand.IN_IDENTIFIER, '')
            try: 
                refId = self.bot.get_proposals_by_id(pid)
                self.bot.command_executor(command_class=ProposalDetailCommand(chat_ids=[self.t_chat["id"]]), refId=refId)
            except Proposal.DoesNotExist:
                self.bot.command_executor(command_class=MessageCommand(chat_ids=[self.t_chat["id"]]), message='Cannot find the detail')
        elif ProtocolProposalsCommand.IN_IDENTIFIER in command:
            cname = command.replace(ProtocolProposalsCommand.IN_IDENTIFIER, '')
            self.bot.command_executor(command_class=ProtocolProposalsCommand(chat_ids=[self.t_chat["id"]]), cname=cname)
        elif ProposalVotesCommand.IN_IDENTIFIER in command:
            pid = command.replace(ProposalVotesCommand.IN_IDENTIFIER, '')
            refId = self.bot.get_proposals_by_id(pid)
            self.bot.command_executor(command_class=ProposalVotesCommand(chat_ids=[self.t_chat["id"]]), refId=refId)
        elif VotersByAddressCommand.IN_IDENTIFIER in command:
            address = command.replace(VotersByAddressCommand.IN_IDENTIFIER, '')
            self.bot.command_executor(command_class=VotersByAddressCommand(chat_ids=[self.t_chat["id"]]), address=address)
        elif ProtocolVotersCommand.IN_IDENTIFIER in command:
            cname = command.replace(ProtocolVotersCommand.IN_IDENTIFIER, '')
            self.bot.command_executor(command_class=ProtocolVotersCommand(chat_ids=[self.t_chat["id"]]), cname=cname)
        elif VotersCommand.IDENTIFIER == command:
            self.bot.command_executor(command_class=VotersCommand(chat_ids=[self.t_chat["id"]]))
        elif VoterDetailCommand.IN_IDENTIFIER in command:
            address = command.replace(VoterDetailCommand.IN_IDENTIFIER, '')
            self.bot.command_executor(command_class=VoterDetailCommand(chat_ids=[self.t_chat["id"]]), address=address)
        else:
            self.bot.command_executor(command_class=HelpCommand(chat_ids=[self.t_chat["id"]]))
            

        return JsonResponse({"ok": "POST request processed"})
    
    
    


