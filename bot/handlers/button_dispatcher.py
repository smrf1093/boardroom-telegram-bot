from django.http import JsonResponse
from telegram import Update
from telegram.ext import CallbackContext

from bot.handlers.bot import Bot
from bot.handlers.button_handlers import (
    ProposalDetailTgView,
    ProposalVotesTgView,
    ProtocolDetailTgView,
    ProtocolProposalsTgView,
    ProtocolsTgView,
    ProtocolVotersTgView,
    StatTgView,
    SubscribeTgView,
    SubscriptionsTgView,
    TopProposalsTgView,
    TopProtocolsTgView,
    UnsubscribeTgView,
    VoterDetailTgView,
    VotersByAddressTgView,
    VotersTgView,
)
from bot.handlers.static_text import BUTTON_ALERTING, BUTTON_STATS
from bot.models import BotChatUser
from .commands import command_start
from .utils import TgUrl, send_typing_action


# Dispatch the button responses.
@send_typing_action
def button_dispatcher(update: Update, context: CallbackContext) -> None:  # noqa: C901
    # User
    user = BotChatUser.get_user(update, context)
    chat_id = user.user_id
    chat = ""
    if not chat:
        chat = {"chat_id": chat_id, "_id": "some id"}

    # Retrieving the message.
    message = update.message
    if not message:
        message = update.edited_message

    # query
    query = update.callback_query
    query.answer()

    # This will define which button the user tapped on (from what you assigned to "callback_data". As I assigned them "1" and "2"):
    choice = query.data

    choice = choice.lstrip("/")
    url = TgUrl.tgurl_load(choice)
    bot = Bot(context.bot)
    print(f"processing choice: {choice} for chat_id: {chat_id}")
    if choice == "start":
        command_start(update, context)
    elif choice == BUTTON_ALERTING:
        user.alerting = not user.alerting
        user.save()
        command_start(update, context)
    elif TopProtocolsTgView.IDENTIFIER in choice:
        bot.send_view(view=TopProtocolsTgView(chat_ids=[chat_id]), url=url)
    elif ProtocolsTgView.IDENTIFIER in choice:
        bot.send_view(view=ProtocolsTgView(chat_ids=[chat_id]), url=url)
    elif SubscriptionsTgView.IDENTIFIER in choice:
        bot.send_view(view=SubscriptionsTgView(chat_ids=[chat_id]), url=url)
    elif choice == BUTTON_STATS:
        bot.send_view(view=StatTgView(chat_ids=[chat_id]), url=url)
    elif ProtocolDetailTgView.IDENTIFIER in choice:
        bot.send_view(view=ProtocolDetailTgView(chat_ids=[chat_id]), url=url)
    elif ProposalDetailTgView.IDENTIFIER in choice:
        bot.send_view(view=ProposalDetailTgView(chat_ids=[chat_id]), url=url)
    elif ProtocolProposalsTgView.IDENTIFIER in choice:
        bot.send_view(view=ProtocolProposalsTgView(chat_ids=[chat_id]), url=url)
    elif TopProposalsTgView.IDENTIFIER in choice:
        bot.send_view(view=TopProposalsTgView(chat_ids=[chat_id]), url=url)
    elif ProposalVotesTgView.IDENTIFIER in choice:
        bot.send_view(view=ProposalVotesTgView(chat_ids=[chat_id]), url=url)
    elif UnsubscribeTgView.IDENTIFIER in choice:
        bot.send_view(view=UnsubscribeTgView(chat_ids=[chat_id]), url=url)
    elif SubscribeTgView.IDENTIFIER in choice:
        bot.send_view(view=SubscribeTgView(chat_ids=[chat_id]), url=url)
    elif VotersByAddressTgView.IDENTIFIER in choice:
        bot.send_view(view=VotersByAddressTgView(chat_ids=[chat_id]), url=url)
    elif ProtocolVotersTgView.IDENTIFIER in choice:
        bot.send_view(view=ProtocolVotersTgView(chat_ids=[chat_id]), url=url)
    elif VoterDetailTgView.IDENTIFIER in choice:
        bot.send_view(view=VoterDetailTgView(chat_ids=[chat_id]), url=url)

    elif VotersTgView.IDENTIFIER in choice:
        bot.send_view(view=VotersTgView(chat_ids=[chat_id]), url=url)

    return JsonResponse({"ok": "POST request processed"})
