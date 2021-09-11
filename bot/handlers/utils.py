import telegram
from functools import wraps
from conf.settings import TELEGRAM_TOKEN, REDIS_URL
from bot.models import BotChatUser
from telegram import MessageEntity
import redis
import json
import time

# Connect to our Redis instance
redis_instance = redis.StrictRedis.from_url(url=REDIS_URL, db=1)

def proposal_refid_truncated(refid):
    """ Get truncated refid"""
    refid_truncated = refid[:50]
    if redis_instance.get(refid_truncated) is None:
        redis_instance.set(refid_truncated, refid)
    return refid_truncated

def proposal_refid(refid_truncated):
    out =  redis_instance.get(refid_truncated)
    if out is not None:
        return out.decode("utf-8")
    return None

def send_typing_action(func):
    """Sends typing action while processing func command."""

    @wraps(func)
    def command_func(update, context, *args, **kwargs):
        context.bot.send_chat_action(chat_id=update.effective_message.chat_id, action=telegram.ChatAction.TYPING)
        return func(update, context,  *args, **kwargs)

    return command_func



def send_message(bot, user_id, text, parse_mode=None, reply_markup=None, reply_to_message_id=None,
                 disable_web_page_preview=None, entities=None):
    try:
        if entities:
            entities = [
                MessageEntity(type=entity['type'],
                              offset=entity['offset'],
                              length=entity['length']
                )
                for entity in entities
            ]

        m = bot.send_message(
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


def cached(ttl_seconds: int = None):
    """
    Decorator that caches the results of the function call.
    
    We use Redis in this example, but any cache (e.g. memcached) will work.
    We also assume that the result of the function can be seralized as JSON,
    which obviously will be untrue in many situations. Tweak as needed.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate the cache key from the function's arguments.
            key_parts = [func.__name__] + list(args[1:])
            key = '-'.join(key_parts)
            result = redis_instance.get(key)

            if result is None:
                # Run the function and cache the result for next time.
                value = func(*args, **kwargs)
                value_json = json.dumps(value)
                redis_instance.set(key, value_json, ex=ttl_seconds)
            else:
                # Skip the function entirely and use the cached value instead.
                print("Cache hit!, loading from cache...")
                value_json = result.decode('utf-8')
                value = json.loads(value_json)

            return value
        return wrapper
    return decorator
