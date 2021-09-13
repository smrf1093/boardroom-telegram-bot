from functools import wraps
import hashlib
import json
import time
from typing import Any, Dict

import redis
import telegram
from telegram import MessageEntity

from bot.models import BotChatUser
from conf.settings import REDIS_URL

# Connect to our Redis instance
redis_instance = redis.StrictRedis.from_url(url=REDIS_URL, db=1)


def postfix(dictionary: Dict[str, Any]) -> str:
    if len(dictionary) == 0:
        return ""
    """MD5 hash of a dictionary."""
    dhash = hashlib.md5()
    # We need to sort arguments so {'a': 1, 'b': 2} is
    # the same as {'b': 2, 'a': 1}
    encoded = json.dumps(dictionary, sort_keys=True).encode()
    dhash.update(encoded)
    return f"_{dhash.hexdigest()}"


class TgUrl:
    path: str
    queries: dict

    def __init__(self, path: str, queries: dict) -> None:
        self.path = path
        self.queries = queries

    def fqdn(self) -> str:
        data = {**self.queries}
        return f"{self.path}{postfix(data)}"

    def get(self) -> None:
        """Get url and save to redis if not exists."""
        fqdn = self.fqdn()
        if redis_instance.get(fqdn) is None:
            redis_instance.set(fqdn, json.dumps({"path": self.path, "queries": self.queries}))
        return fqdn

    @classmethod
    def tgurl_load(cls, fqdn: str) -> Any:
        out = redis_instance.get(fqdn)
        if out is not None:
            data = json.loads(out.decode("utf-8"))
            return TgUrl(data["path"], data["queries"])
        return None


def send_typing_action(func):
    """Sends typing action while processing func command."""

    @wraps(func)
    def command_func(update, context, *args, **kwargs):
        context.bot.send_chat_action(
            chat_id=update.effective_message.chat_id, action=telegram.ChatAction.TYPING
        )
        return func(update, context, *args, **kwargs)

    return command_func


def send_message(
    bot,
    user_id,
    text,
    parse_mode=None,
    reply_markup=None,
    reply_to_message_id=None,
    disable_web_page_preview=None,
    entities=None,
):
    try:
        if entities:
            entities = [
                MessageEntity(
                    type=entity["type"], offset=entity["offset"], length=entity["length"]
                )
                for entity in entities
            ]

        bot.send_message(
            chat_id=user_id,
            text=text,
            parse_mode=parse_mode,
            reply_markup=reply_markup,
            reply_to_message_id=reply_to_message_id,
            disable_web_page_preview=disable_web_page_preview,
            entities=entities,
        )
    except telegram.error.Unauthorized:
        print(f"Can't send message to {user_id}. Reason: Bot was stopped.")
        BotChatUser.objects.filter(user_id=user_id).update(is_blocked_bot=True)
        success = False
    except Exception as e:
        print(f"Can't send message to {user_id}. Reason: {e}")
        success = False
    except telegram.error.RetryAfter as e:
        print(f"Can't send message to {user_id}. Reason: {e}")
        time.sleep(e.retry_after)
    else:
        success = True
        BotChatUser.objects.filter(user_id=user_id).update(is_blocked_bot=False)
    return success
