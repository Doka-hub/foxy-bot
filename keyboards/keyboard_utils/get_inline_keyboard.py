from typing import List

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_inline_keyboard(data: List[List[InlineKeyboardButton]]):
    inline_keyboard = InlineKeyboardMarkup()
    for row in data:
        inline_keyboard.row(*row)
    return inline_keyboard
