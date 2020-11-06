from typing import List

import logging

from asyncio import sleep

from aiogram.utils.exceptions import RetryAfter, CantParseEntities

from models import objects, Channel, Article

from utils.db_api.user.channel import get_channel, check_user_channel_subscribed

from loader import bot


logging.basicConfig(level=logging.INFO)


def make_message(language: str, preview_text: str, article_url: str, category: str) -> str:
    ru_message = preview_text + f'\n\n#' + category.replace('_', '\_') + '\n\n' + f'[Читать...]({article_url})'
    en_message = preview_text + f'\n\n#' + category.replace('_', '\_') + '\n\n' + f'[Read...]({article_url})'
    he_message = preview_text + f'\n\n#' + category.replace('_', '\_') + '\n\n' + f'[Read...]({article_url})'
    return (
        ru_message if language == 'ru' else
        en_message if language == 'en' else
        he_message
    )


async def send_post_to_channel(language: str, preview_text: str, article_url: str, category: str) -> None:
    channel = await objects.get(Channel, language=language)
    channel_id = channel.channel_id

    message = make_message(language, preview_text, article_url, category)
    try:
        try:
            await bot.send_message(channel_id, message,
                                   parse_mode='markdown', disable_notification=True)
        except RetryAfter:
            await sleep(65.0)
            try:
                await bot.send_message(channel_id, make_message(language, preview_text, article_url, category),
                                       parse_mode='markdown', disable_notification=True)
            except RetryAfter:
                await sleep(5.0)
                try:
                    await bot.send_message(channel_id, make_message(language, preview_text, article_url, category),
                                           parse_mode='markdown', disable_notification=True)
                except RetryAfter:
                    pass
    except CantParseEntities as e:  # если какой-то символ нельзя писать в тг
        logging.info(f'{e} - {preview_text} - {article_url}')
        try:
            await bot.send_message(channel_id, make_message(language, '', article_url, category),
                                   parse_mode='markdown', disable_notification=True)
        except RetryAfter:
            await sleep(5.0)
        except CantParseEntities as e:  # если какой-то символ нельзя писать в тг
            logging.info(f'{e} - {article_url}')


async def send_post_to_user(user_id: int, language: str, article_url: str, category: str) -> None:
    message = make_message(language, '', article_url, category)
    try:
        await bot.send_message(user_id, message,
                               parse_mode='markdown')
    except RetryAfter:
        await sleep(65.0)
        try:
            await bot.send_message(user_id, message,
                                   parse_mode='markdown', disable_notification=True)
        except RetryAfter:
            await sleep(5.0)
            try:
                await bot.send_message(user_id, message,
                                       parse_mode='markdown', disable_notification=True)
            except RetryAfter:
                pass
    except CantParseEntities as e:
        logging.info(f'{e} - {category}')


async def send_post_news_teller(time_to_mail: str) -> None:
    for article in await objects.execute(Article.select()):
        for user in article.category.users:
            article_language = article.category.language

            channel = await get_channel(article_language)
            channel_id = channel.channel_id

            if await check_user_channel_subscribed(user.user_id, channel_id):
                if user.time_to_mail == time_to_mail:
                    await send_post_to_user(user.user_id, article.category.language, article.url, article.category.name)
    if time_to_mail == 'morning':  # очищаем статьи после утренней рассылки
        Article.truncate_table()


async def send_post_news_teller_upon_receipt_of(articles: List[Article]) -> None:
    for article in articles:
        for user in article.category.users:
            article_language = article.category.language

            channel = await get_channel(article_language)
            channel_id = channel.channel_id

            if await check_user_channel_subscribed(user.user_id, channel_id):
                await send_post_to_user(user.user_id, article.category.language, article.url, article.category.name)
