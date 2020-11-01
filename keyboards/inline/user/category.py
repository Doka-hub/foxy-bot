from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from models import objects, Channel, Category

from utils.keyboards.inline import get_inline_keyboard
from utils.db_api.user.user import get_or_create_user

from data import config


def get_channel_check_subscribe_inline_keyboard(user_language: str,
                                                channel_to_subscribe: Channel) -> InlineKeyboardMarkup:
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


async def get_categories_inline_keyboard(user_id: int) -> InlineKeyboardMarkup:
    user, created = await get_or_create_user(user_id)
    user_language = user.language
    subscribed_categories = user.subscribed

    categories = await objects.execute(Category.select().where(Category.language == user_language))
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
                    callback_data='menu'
                )
            ]
        ]
    )
    return categories_inline_keyboard


async def get_time_to_mail_inline_keyboard(user_id: int) -> InlineKeyboardMarkup:
    user, created = await get_or_create_user(user_id)
    user_language = user.language
    user_time_to_mail = user.time_to_mail

    morning = config.messages[user_language]['time_to_mail']['morning']
    evening = config.messages[user_language]['time_to_mail']['evening']
    upon_receipt_of = config.messages[user_language]['time_to_mail']['upon_receipt_of']

    time_to_mail_inline_keyboard = get_inline_keyboard(
        [
            [
                InlineKeyboardButton(
                    f'• {morning}' if user_time_to_mail == 'morning' else morning,
                    callback_data='choose_time_to_mail morning'
                ),
                InlineKeyboardButton(
                    f'• {evening}' if user_time_to_mail == 'evening' else evening,
                    callback_data='choose_time_to_mail evening'
                )
            ],
            [
                InlineKeyboardButton(
                    f'• {upon_receipt_of}' if user_time_to_mail == 'upon_receipt_of' else upon_receipt_of,
                    callback_data='choose_time_to_mail upon_receipt_of'
                )
            ],
            [
                InlineKeyboardButton(
                    config.messages[user_language]['menu']['back'], callback_data='menu'
                )
            ]
        ]
    )
    return time_to_mail_inline_keyboard
