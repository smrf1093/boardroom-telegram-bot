from .bot_commands import Command, StartCommand, ProposalsJsonCommand
import requests
import time 
import json
# api.telegram.org/bot<your_token>/setWebHook?url=https://<your_ngrok_url.ngrok.io/
# api.telegram.org/bot1994698934:AAE1EGF_CDsOfrA5_zwbo1lz93LpL5KEvLw/setWebHook?url=https://1039-2a01-7e01-00-f03c-92ff-fe30-eb94.ngrok.io

class _Bot():
    TELEGRAM_URL = "https://api.telegram.org/bot"
    MAX_MESSAGE_LENGTH = 4000
    def __init__(self) -> None:
        self.token = '1994698934:AAE1EGF_CDsOfrA5_zwbo1lz93LpL5KEvLw'


    def command_executor(self, command_class: Command, **kwargs):
        """
            chat_id: the receiver 
            command_class: the Command Class 
        """
        if type(Command) != StartCommand:
            self.send_wait_message(chat_id=command_class.chat_id)
        self.send_chunk_message(chat_id=command_class.chat_id, text=command_class.execute(**kwargs))


    # TODO: here the results should be cached 
    def get_proposals_by_id(self, pid):
        """
            pid: proposal id 
        """
        proposals = ProposalsJsonCommand(chat_ids=[]).execute()
        for proposal in proposals:
            if proposal['id'].lower() == pid:
                return proposal['refId']
        return None


    def bulk_command_executor(self, command_class: Command, **kwargs):
        """
            chat_ids: list of all subscribers
            command_class: the class that should call the API
        """
        api_response_as_text  = command_class.execute(**kwargs)
        for chat_id in command_class.chat_ids:
            self.send_chunk_message(chat_id=chat_id, text=api_response_as_text)
    
    def send_wait_message(self, chat_id):
        msg = 'Please wait...'
        self.send_message(msg, chat_id)
    
    def send_chunk_message(self, chat_id, text: str, **kwargs):
        if len(text) <= _Bot.MAX_MESSAGE_LENGTH:
            return self.send_message(text, chat_id)

        parts = []
        while len(text) > 0:
            if len(text) > _Bot.MAX_MESSAGE_LENGTH:
                part = text[:_Bot.MAX_MESSAGE_LENGTH]
                first_lnbr = part.rfind('\n')
                if first_lnbr != -1:
                    parts.append(part[:first_lnbr])
                    text = text[first_lnbr:]
                else:
                    parts.append(part)
                    text = text[_Bot.MAX_MESSAGE_LENGTH:]
            else:
                parts.append(text)
                break

        msg = None
        for part in parts:
            msg = self.send_message(part, chat_id)
            time.sleep(1)
        return msg  # return only the last message

    def send_message(self, message, chat_id):
        data = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "Markdown",
        }
        requests.post(
            f"{_Bot.TELEGRAM_URL}{self.token}/sendMessage", data=data
        )
        

instance = None

def Bot():
    global instance
    if instance:
        return instance
    return _Bot()