from .bot_commands import Command, StartCommand
import requests

# api.telegram.org/bot<your_token>/setWebHook?url=https://<your_ngrok_url.ngrok.io/
# api.telegram.org/bot1994698934:AAE1EGF_CDsOfrA5_zwbo1lz93LpL5KEvLw/setWebHook?url=https://7db4-5-239-123-132.ngrok.io 

class _Bot():
    TELEGRAM_URL = "https://api.telegram.org/bot"
    
    def __init__(self, chat_id) -> None:
        self.token = '1994698934:AAE1EGF_CDsOfrA5_zwbo1lz93LpL5KEvLw'
        self.chat_id = chat_id
        
    
    def command_executor(self, command_class: Command, **kwargs):
        if type(Command) != StartCommand:
            self.send_wait_message()
        self.send_message(command_class.execute(**kwargs))
    
    def send_wait_message(self):
        msg = 'Please wait...'
        self.send_message(msg)
    
    def send_message(self, message):
        data = {
            "chat_id": self.chat_id,
            "text": message,
            "parse_mode": "Markdown",
        }
        requests.post(
            f"{_Bot.TELEGRAM_URL}{self.token}/sendMessage", data=data
        )
        

instance = None

def Bot(chat_id):
    global instance
    if instance:
        return instance
    return _Bot(chat_id=chat_id)