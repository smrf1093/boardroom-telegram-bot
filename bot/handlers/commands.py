from .boardroom_api_client import BroadroomAPIClient
from abc import ABC
import bot.handlers.static_text
from telegram import ReplyKeyboardMarkup, Update, ReplyKeyboardRemove
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackContext,
)
from .button_handlers import ProtocolsButton, VotersButton, SubscriptionsButton
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from bot.handlers.static_text import BUTTON_ALERTING, BUTTON_CONFIRM, BUTTON_STATS, BUTTON_DECLINE, confirm, decline, \
start, subscriptions, protocols, voters, toggle_alerting, stats, enabled, disabled, top_protocols, top_proposals


from bot.models import BotChatUser

def command_start(update, context):
    u, _ = BotChatUser.get_user_and_created(update, context)
    text = start.format(username=u.username, alerting=enabled if u.alerting else disabled)


    context.bot.send_message(u.user_id, text=text,
                              reply_markup=make_keyboard_for_start_command())



def make_keyboard_for_start_command():
    buttons = [
        [InlineKeyboardButton(toggle_alerting, callback_data=f'{BUTTON_ALERTING}')],
        [InlineKeyboardButton(subscriptions, callback_data=SubscriptionsButton.IDENTIFIER)],
        [InlineKeyboardButton(top_protocols, callback_data=TopProtocolsButton.IDENTIFIER)],
        [InlineKeyboardButton(top_proposals, callback_data=TopProposalsButton.IDENTIFIER)],
        [InlineKeyboardButton(protocols, callback_data=ProtocolsButton.IDENTIFIER)],
        [InlineKeyboardButton(voters, callback_data=VotersButton.IDENTIFIER)],
        [InlineKeyboardButton(stats, callback_data=f'{BUTTON_STATS}')],
    ]

    return InlineKeyboardMarkup(buttons)


def keyboard_confirm_decline():
    buttons = [[
        InlineKeyboardButton(confirm, callback_data=f'{BUTTON_CONFIRM}'),
        InlineKeyboardButton(decline, callback_data=f'{BUTTON_DECLINE}')
    ]]

    return InlineKeyboardMarkup(buttons)