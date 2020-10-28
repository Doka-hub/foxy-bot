from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from utils.keyboards.inline import get_inline_keyboard

from models import objects, InfoArticle

from data import config


async def get_info_inline_keyboard(user_language: str) -> InlineKeyboardMarkup:
    info_articles = await objects.execute(InfoArticle.select().where(InfoArticle.language == user_language))

    articles = [
        [
            InlineKeyboardButton(
                info_article.title, url=info_article.url
            )
        ] for info_article in info_articles
    ]

    info_inline_keyboard = get_inline_keyboard(
        articles + [
            [
                InlineKeyboardButton(
                    config.messages[user_language]['menu']['back'],
                    callback_data='menu'
                )
            ]
        ]
    )
    return info_inline_keyboard
