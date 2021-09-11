from bot.handlers.static_text import BUTTON_ALERTING, BUTTON_STATS
from django.http import JsonResponse
from telegram import Update
from telegram.ext import (
    CallbackContext,
)
from .commands import command_start
from bot.handlers.bot import Bot
from bot.handlers.button_handlers import (
    ProtocolsButton,
    ProtocolDetailButton, 
    ProposalDetailButton,
    ProtocolProposalsButton,
    MessageButton,
    ProposalVotesButton,
    StatButton,
    SubscribeButton,
    UnsubscribeButton,
    VotersByAddressButton,
    ProtocolVotersButton,
    VotersButton,
    VoterDetailButton,
    SubscriptionsButton,
)
from bot.models import (
    BotChatUser,
)
from .utils import proposal_refid, send_typing_action

# Dispatch the button responses.
@send_typing_action
def button_dispatcher(update: Update, context: CallbackContext) -> None: 
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

    bot = Bot(context.bot)
    print(f"processing choice: {choice} for chat_id: {chat_id}")
    if choice == "start":
        command_start(update, context)
    elif choice == BUTTON_ALERTING:
        user.alerting = not user.alerting
        user.save()
        command_start(update, context)
    elif choice == ProtocolsButton.IDENTIFIER:
        bot.process_action(button=ProtocolsButton(chat_ids=[chat_id]))
    elif choice == SubscriptionsButton.IDENTIFIER:
        bot.process_action(button=SubscriptionsButton(chat_ids=[chat_id]))
    elif choice == BUTTON_STATS:
        bot.process_action(button=StatButton(chat_ids=[chat_id]))
    elif ProtocolDetailButton.IN_IDENTIFIER in choice:
        # remove command identifier
        cname = choice.replace(ProtocolDetailButton.IN_IDENTIFIER, '')
        bot.process_action(button=ProtocolDetailButton(chat_ids=[chat_id]), cname=cname)
    elif ProposalDetailButton.IN_IDENTIFIER in choice: 
        # remove the identifier 
        refid_truncated = choice.replace(ProposalDetailButton.IN_IDENTIFIER, '')
        refId = proposal_refid(refid_truncated)
        bot.process_action(button=ProposalDetailButton(chat_ids=[chat_id]), refId=str(refId))
    elif ProtocolProposalsButton.IN_IDENTIFIER in choice:
        cname = choice.replace(ProtocolProposalsButton.IN_IDENTIFIER, '')
        bot.process_action(button=ProtocolProposalsButton(chat_ids=[chat_id]), cname=cname)
    elif ProposalVotesButton.IN_IDENTIFIER in choice:
        refid_truncated = choice.replace(ProposalVotesButton.IN_IDENTIFIER, '')
        refId = proposal_refid(refid_truncated)
        bot.process_action(button=ProposalVotesButton(chat_ids=[chat_id]), refId=refId)
    elif UnsubscribeButton.IDENTIFIER in choice:
        refid_truncated = choice.replace(UnsubscribeButton.IDENTIFIER, '')
        refId = proposal_refid(refid_truncated)
        bot.process_action(button=UnsubscribeButton(chat_ids=[chat_id]), refId=refId)
    elif SubscribeButton.IDENTIFIER in choice:
        refid_truncated = choice.replace(SubscribeButton.IDENTIFIER, '')
        refId = proposal_refid(refid_truncated)
        bot.process_action(button=SubscribeButton(chat_ids=[chat_id]), refId=refId)
    elif VotersByAddressButton.IN_IDENTIFIER in choice:
        address = choice.replace(VotersByAddressButton.IN_IDENTIFIER, '')
        bot.process_action(button=VotersByAddressButton(chat_ids=[chat_id]), address=address)
    elif ProtocolVotersButton.IN_IDENTIFIER in choice:
        cname = choice.replace(ProtocolVotersButton.IN_IDENTIFIER, '')
        bot.process_action(button=ProtocolVotersButton(chat_ids=[chat_id]), cname=cname)
    elif VotersButton.IDENTIFIER == choice:
        bot.process_action(button=VotersButton(chat_ids=[chat_id]))
    elif VoterDetailButton.IN_IDENTIFIER in choice:
        address = choice.replace(VoterDetailButton.IN_IDENTIFIER, '')
        bot.process_action(button=VoterDetailButton(chat_ids=[chat_id]), address=address)

    return JsonResponse({"ok": "POST request processed"})





