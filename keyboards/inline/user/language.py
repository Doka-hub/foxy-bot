from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from utils.keyboards.inline import get_inline_keyboard


def get_language_inline_keyboard() -> InlineKeyboardMarkup:
    language_inline_keyboard = get_inline_keyboard(
        [
            [InlineKeyboardButton('🇷🇺 русский', callback_data='choose_language ru')],
            [InlineKeyboardButton('🇺🇸 english', callback_data='choose_language en')],
            [InlineKeyboardButton('🇮🇱 עברית', callback_data='choose_language he')]
        ]
    )
    return language_inline_keyboard
