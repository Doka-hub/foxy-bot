from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from models import objects, Channel, Category

from utils.keyboards.inline import get_inline_keyboard
from utils.db_api.users import get_or_create_user

from data import config


def get_check_subscribe_inline_keyboard(user_language: str, channel_to_subscribe: Channel) -> InlineKeyboardMarkup:
    check_subscribe_inline_keyboard = get_inline_keyboard(
        [
            [
                InlineKeyboardButton(
                    config.messages[user_language]['check_subscribe'],
                    callback_data=f'check_subscribe {channel_to_subscribe.channel_id}'
                )
            ]
        ]
    )
    return check_subscribe_inline_keyboard


async def get_categories_inline_keyboard(user_id: int):
    user, created = await get_or_create_user(user_id)
    user_language = user.language
    subscribed_categories = user.subscribed

    categories = await objects.execute(Category.select().where(Category.language == user[0].language))
    category_list = [
        [
            InlineKeyboardButton(
                category.name.replace('_', ' ') if category not in subscribed_categories else
                f'• {category.name.replace("_", " ")}',
                callback_data=f'choose_category {category.key}'
            )
        ] for category in categories
    ]

    categories_inline_keyboard = get_inline_keyboard(
        category_list + [
            [
                InlineKeyboardButton(
                    config.messages[user_language]['menu']['back'],
                    callback_data='back_to_menu'
                )
            ]
        ]
    )
    return categories_inline_keyboard
