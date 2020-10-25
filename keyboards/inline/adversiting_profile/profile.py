from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from utils.keyboards.inline import get_inline_keyboard

from data import config


async def get_advertising_profile_inline_keyboard(user_language: str) -> InlineKeyboardMarkup:
    advertising_profile_menu = config.messages[user_language]['advertising_profile']

    advertising_profile_inline_keyboard = get_inline_keyboard(
        [
            [
                InlineKeyboardButton(
                    advertising_profile_menu['my_posts'], callback_data='post_list'
                ),
            ],
            [
                InlineKeyboardButton(
                    advertising_profile_menu['create_post'], callback_data='create_post'
                )
            ],
            [
                InlineKeyboardButton(
                    config.messages[user_language]['menu']['back'], callback_data='menu'
                )
            ],
        ]
    )
    return advertising_profile_inline_keyboard
