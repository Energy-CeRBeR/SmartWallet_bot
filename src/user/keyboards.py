from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from src.user.lexicon import LEXICON


def create_stop_keyboard() -> InlineKeyboardMarkup:
    stop_button = InlineKeyboardButton(
        text=LEXICON["exit_process"],
        callback_data="stop_all_processes"
    )

    keyboard = InlineKeyboardMarkup(inline_keyboard=[[stop_button]])

    return keyboard
