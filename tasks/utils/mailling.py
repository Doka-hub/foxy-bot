import logging

from datetime import date, datetime

from typing import List, Union, Optional

from asyncio import sleep

from aiogram.utils.exceptions import RetryAfter, CantParseEntities, BotBlocked, ChatNotFound
from aiogram.types import InlineKeyboardMarkup

from models import objects, Channel, Article, Post, TGUser

from utils.db_api.user.channel import get_channel, check_user_channel_subscribed
from keyboards.inline.adversiting_profile.post import get_post_button_inline_keyboard

from loader import bot

from data import config


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


async def send_message(to: Union[str, int], text: Optional[str] = None, image_id: Optional[str] = None,
                       parse_mode: Optional[str] = None, reply_markup: Optional[InlineKeyboardMarkup] = None,
                       disable_notification: Optional[bool] = True, made_tries: int = 0, max_tries: int = 5) -> bool:
    """

    :param to:
    :param text:
    :param image_id:
    :param parse_mode:
    :param reply_markup:
    :param disable_notification: отключаем звук
    :param made_tries: `n` совершенных проб
    :param max_tries: пробуем отправить сообщение максимум `n` раз
    :return:
    """
    if made_tries >= 5:
        return False
    try:
        if image_id:
            await bot.send_photo(to, image_id, text, parse_mode=parse_mode, reply_markup=reply_markup,
                                 disable_notification=disable_notification)
        else:
            await bot.send_message(to, text, parse_mode=parse_mode, reply_markup=reply_markup,
                                   disable_notification=disable_notification)
    except RetryAfter as e:
        error = f'{e}'
        time = error[error.find('Retry in ') + len('Retry in '):error.find(' seconds')]  # сколько нужно ждать
        await sleep(float(time))
        await send_message(to, text, image_id, parse_mode, reply_markup, disable_notification, made_tries+1, max_tries)
        return False
    return True


async def send_post_to_channel(language: str, preview_text: str, article_url: str, category: str) -> None:
    channel = await objects.get(Channel, language=language)
    channel_id = channel.channel_id

    message = make_message(language, preview_text, article_url, category)
    try:
        await send_message(channel_id, message, None, 'markdown')
    except CantParseEntities as e:  # если какой-то символ нельзя писать в тг
        logging.info(f'{e} - {preview_text} - {article_url}')

        message = make_message(language, '', article_url, category)
        await send_message(channel_id, message, None, 'markdown')


async def send_post_to_user(user_id: int, language: str, article_url: str, category: str) -> None:
    message = make_message(language, '', article_url, category)
    try:
        await send_message(user_id, message, None, 'markdown')
    except CantParseEntities as e:
        logging.info(f'{e} - {article_url} - {category}')


async def send_advertising_post_to_channel(channel_id: Union[str, int], advertising_post: Post) -> None:
    image_id = advertising_post.get_image()
    text = advertising_post.text
    post_button_inline_keyboard = await get_post_button_inline_keyboard(advertising_post.button)

    sent = await send_message(channel_id, text, image_id, 'markdown', post_button_inline_keyboard)
    if sent:
        advertising_post.status = 'posted'
        await objects.update(advertising_post, ['status'])


async def send_advertising_post_to_user(user_id: int, advertising_post: Post) -> None:
    image_id = advertising_post.image_id
    text = advertising_post.text
    post_button_inline_keyboard = await get_post_button_inline_keyboard(advertising_post.button)

    await send_message(user_id, text, image_id, 'markdown', post_button_inline_keyboard)


async def send_post_news_teller(time_to_mail: str) -> None:
    expression = [Post.paid, Post.status == 'accepted', Post.date == date.today(), Post.time == time_to_mail]
    for advertising_post in await objects.execute(Post.select().where(*expression)):
        channel_id = advertising_post.channel.channel_id
        await send_advertising_post_to_channel(channel_id, advertising_post)

        for user in await objects.execute(TGUser.select().where(TGUser.blocked_by_user == False)):
            if user.language == advertising_post.channel.language:
                try:
                    await send_advertising_post_to_user(user.user_id, advertising_post)
                except BotBlocked:
                    user.blocked_by_user = True
                    await objects.update(user, ['blocked_by_user'])
                except ChatNotFound:
                    pass
                except Exception as e:
                    logging.info(f'{datetime.today()}: {e} - {user}')
                    for admin in config.ADMINS.values():
                        await bot.send_message(admin, f'{datetime.today()}: {e} - {user}')

    for article in await objects.execute(Article.select()):
        for user in article.category.users.where(TGUser.blocked_by_user == False):
            article_language = article.category.language

            channel = await get_channel(article_language)
            channel_id = channel.channel_id

            if await check_user_channel_subscribed(user.user_id, channel_id):
                if user.time_to_mail == time_to_mail:
                    user_id = user.user_id
                    language = article.category.language
                    article_url = article.url
                    category_name = article.category.name
                    try:
                        await send_post_to_user(user_id, language, article_url, category_name)
                    except BotBlocked:
                        user.blocked_by_user = True
                        await objects.update(user, ['blocked_by_user'])
                    except ChatNotFound as e:
                        logging.info(f'{datetime.today()}: {e} - {user}')
                        for admin in config.ADMINS.values():
                            await bot.send_message(admin, f'{datetime.today()}: {e} - {user}')
                    except Exception as e:
                        logging.info(f'{datetime.today()}: {e} - {user}')
                        for admin in config.ADMINS.values():
                            await bot.send_message(admin, f'{datetime.today()}: {e} - {user}')

    if time_to_mail == 'morning':  # очищаем статьи после утренней рассылки
        Article.truncate_table()


async def send_post_news_teller_upon_receipt_of(articles: List[Article]) -> None:
    for article in articles:
        for user in article.category.users:
            article_language = article.category.language

            channel = await get_channel(article_language)
            channel_id = channel.channel_id

            if await check_user_channel_subscribed(user.user_id, channel_id):
                if user.time_to_mail == 'upon_receipt_of':
                    await send_post_to_user(user.user_id, article.category.language,
                                            article.url, article.category.name)
