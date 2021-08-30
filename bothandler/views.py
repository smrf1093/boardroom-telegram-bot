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
    ProposalDetailCommand
)
from bothandler.models import Proposal
# Create your views here.
from django.views import View

class BroadroomView(View):

    def post(self, request, *args, **kwargs):
        
        self.t_data = json.loads(request.body)
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
        self.bot = Bot(chat_id=self.t_chat["id"])
        if command == "start":
            self.bot.command_executor(StartCommand())
        elif command == "protocols":
            self.bot.command_executor(ProtocolsCommand())
        elif 'pdetail' in command:
            cname = command.replace('pdetail', '')
            self.bot.command_executor(ProtocolDetailCommand(), cname=cname)
        elif command == "proposals":
            self.bot.command_executor(ProposalsCommand())
        elif 'refid' in command: 
            refId = command.replace('refid', '')
            try: 
                proposal = Proposal.objects.get(p_id=refId)
                print(proposal.ref_id)
                self.bot.command_executor(ProposalDetailCommand(), refId=proposal.ref_id)
            except Proposal.DoesNotExist:
                print('Not Found')
                pass
        else:
            self.bot.command_executor(HelpCommand())
            

        return JsonResponse({"ok": "POST request processed"})
    
    
    


