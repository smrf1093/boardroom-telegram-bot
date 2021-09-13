from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from bot.handlers.static_text import (
    BUTTON_ALERTING,
    BUTTON_CONFIRM,
    BUTTON_DECLINE,
    BUTTON_STATS,
    confirm,
    decline,
    disabled,
    enabled,
    protocols,
    start,
    stats,
    subscriptions,
    toggle_alerting,
    top_proposals,
    top_protocols,
    voters,
)
from bot.models import BotChatUser
from .button_handlers import (
    ProtocolsTgView,
    SubscriptionsTgView,
    TopProposalsTgView,
    TopProtocolsTgView,
    VotersTgView,
)
from .utils import TgUrl


def command_start(update, context):
    u, _ = BotChatUser.get_user_and_created(update, context)
    text = start.format(username=u.username, alerting=enabled if u.alerting else disabled)

    context.bot.send_message(u.user_id, text=text, reply_markup=make_keyboard_for_start_command())


def make_keyboard_for_start_command():
    buttons = [
        [InlineKeyboardButton(toggle_alerting, callback_data=f"{BUTTON_ALERTING}")],
        [
            InlineKeyboardButton(
                subscriptions, callback_data=TgUrl(SubscriptionsTgView.IDENTIFIER, {}).get()
            )
        ],
        [
            InlineKeyboardButton(
                top_protocols, callback_data=TgUrl(TopProtocolsTgView.IDENTIFIER, {}).get()
            )
        ],
        [
            InlineKeyboardButton(
                top_proposals, callback_data=TgUrl(TopProposalsTgView.IDENTIFIER, {}).get()
            )
        ],
        [
            InlineKeyboardButton(
                protocols, callback_data=TgUrl(ProtocolsTgView.IDENTIFIER, {}).get()
            )
        ],
        [InlineKeyboardButton(voters, callback_data=TgUrl(VotersTgView.IDENTIFIER, {}).get())],
        [InlineKeyboardButton(stats, callback_data=TgUrl(f"{BUTTON_STATS}", {}).get())],
    ]

    return InlineKeyboardMarkup(buttons)


def keyboard_confirm_decline():
    buttons = [
        [
            InlineKeyboardButton(confirm, callback_data=f"{BUTTON_CONFIRM}"),
            InlineKeyboardButton(decline, callback_data=f"{BUTTON_DECLINE}"),
        ]
    ]

    return InlineKeyboardMarkup(buttons)
