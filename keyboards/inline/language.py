from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_language_inline_keyboard():
    language_inline_keyboard = InlineKeyboardMarkup()
    language_inline_keyboard.add(
        [InlineKeyboardButton('🇷🇺 русский', callback_data='choose_language ru')],
        [InlineKeyboardButton('🇺🇸 english', callback_data='choose_language en')],
        [InlineKeyboardButton('🇮🇱 עברית', callback_data='choose_language he')]
    )
    return language_inline_keyboard
