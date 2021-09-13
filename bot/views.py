import json
import logging

from django.http import JsonResponse
from django.views import View

from bot.handlers.dispatcher import TELEGRAM_BOT_USERNAME, process_telegram_event
from conf.settings import DEBUG

logger = logging.getLogger(__name__)

BOT_URL = f"https://t.me/{TELEGRAM_BOT_USERNAME}"


def index(request):
    return JsonResponse({"error": "sup hacker"})


class TelegramBotWebhookView(View):
    # WARNING: if fail - Telegram webhook will be delivered again.
    # Can be fixed with async celery task execution
    def post(self, request, *args, **kwargs):
        if DEBUG:
            process_telegram_event(json.loads(request.body))
        else:  # use celery in production
            process_telegram_event.delay(json.loads(request.body))

        # TODO: there is a great trick to send data in webhook response
        # e.g. remove buttons
        return JsonResponse({"ok": "POST request processed"})

    def get(self, request, *args, **kwargs):  # for debug
        return JsonResponse({"ok": "Get request processed. But nothing done"})
