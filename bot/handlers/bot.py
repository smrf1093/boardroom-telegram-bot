import time

from celery.utils.log import get_task_logger
import telegram
from telegram.inline.inlinekeyboardmarkup import InlineKeyboardMarkup

from bot.handlers.boardroom_api_client import BroadroomAPIClient
from bot.handlers.button_handlers import TgResponse, TgView
from bot.handlers.utils import TgUrl
from bot.models import BotChatUser

logger = get_task_logger(__name__)

MAX_MESSAGE_LENGTH = 4000


class BotWrapper:
    def __init__(self, bot) -> None:
        self.bot = bot
        self.api_client = BroadroomAPIClient()

    def send_view(self, view: TgView, url: TgUrl):
        """
        chat_id: the receiver
        button: the tapped button
        """
        self.send_chunk_message(chat_id=view.chat_id, tg_response=view.execute(url))

    def send_bulk(self, view: TgView, url: TgUrl):
        """
        chat_ids: list of all subscribers
        button: the button instance that will call the API
        """
        response = view.execute(url)
        for chat_id in view.chat_ids:
            try:
                self.send_chunk_message(chat_id=chat_id, tg_response=response)
                # logger.info(f"Broadcast message was sent to {chat_id}")
            except Exception as e:
                logger.error(f"Failed to send message to {chat_id}, reason: {e}")

    def send_chunk_message(self, chat_id, tg_response: TgResponse, **kwargs):
        parts = []
        if len(tg_response.message) <= MAX_MESSAGE_LENGTH:
            parts = [tg_response.message]
        else:
            text = tg_response.message
            while len(text) > 0:
                if len(text) > MAX_MESSAGE_LENGTH:
                    part = text[:MAX_MESSAGE_LENGTH]
                    first_lnbr = part.rfind("\n")
                    if first_lnbr != -1:
                        parts.append(part[:first_lnbr])
                        text = text[first_lnbr:]
                    else:
                        parts.append(part)
                        text = text[MAX_MESSAGE_LENGTH:]
                else:
                    parts.append(text)
                    break

        for i, part in enumerate(parts):
            try:
                kwargs = {
                    "chat_id": chat_id,
                    "text": part,
                    "parse_mode": telegram.ParseMode.MARKDOWN,
                }
                # Sending the keyboards in the last message
                if i == len(parts) - 1 and len(tg_response.keyboards) > 0:
                    kwargs["reply_markup"] = InlineKeyboardMarkup(tg_response.keyboards)
                self.bot.send_message(**kwargs)

            except telegram.error.Unauthorized:
                print(f"Can't send message to {chat_id}. Reason: Bot was stopped by the user.")
                BotChatUser.objects.filter(user_id=chat_id).update(is_blocked_bot=True)
            except telegram.error.RetryAfter as e:
                print(f"Can't send message to {chat_id}. Reason: {e}")
                time.sleep(e.retry_after)


instance = None


def Bot(bot):
    global instance
    if instance:
        return instance
    return BotWrapper(bot)
