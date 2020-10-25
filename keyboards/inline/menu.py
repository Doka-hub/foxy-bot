from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from data import config
from utils.keyboards.inline import get_inline_keyboard


def get_menu_inline_keyboard(user_language: str) -> InlineKeyboardMarkup:
    menu = config.messages[user_language]['menu']
    menu_inline_keyboard = get_inline_keyboard([
            [InlineKeyboardButton(menu['change_language'], callback_data='change_language')],
            [InlineKeyboardButton(menu['category_list'], callback_data='category_list')],
            [InlineKeyboardButton(menu['show_time_to_mail'], callback_data='show_time_to_mail')],
            [InlineKeyboardButton(menu['advertising_profile'], callback_data='advertising_profile')],
            [InlineKeyboardButton(menu['info'], callback_data='info')],
    ])
    return menu_inline_keyboard
