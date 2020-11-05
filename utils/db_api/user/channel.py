import logging

from typing import Optional

from aiogram import bot as Bot
from aiogram.utils.exceptions import BadRequest

from models import objects, Channel

from .user import get_or_create_user
from .language import get_language


logging.basicConfig(level=logging.INFO, filename='bot_logs/member.log')


async def get_channel_to_subscribe(language: Optional[str] = None, channel_id: Optional[int] = None) -> Channel:
    if language:
        channel = await objects.get(Channel, language=language)
    else:
        channel = await objects.get(Channel, channel_id=channel_id)
    return channel


async def check_user_channel_subscribed(bot: Bot, user_id: int, channel_id: int = None) -> bool:
    if not channel_id:
        user_language = await get_language(user_id)
        channel = await get_channel_to_subscribe(user_language)
        channel_id = channel.channel_id

    try:
        member = await bot.get_chat_member(channel_id, user_id)
        logging.info(member)
        return True if member.status == 'member' else False
    except BadRequest:  # если участник не найден
        return False


async def subscribe_user_to_channel(user_id: int, channel_id: int) -> None:
    user, created = await get_or_create_user(user_id)
    channel = await get_channel_to_subscribe(channel_id=channel_id)

    if channel.language == 'ru':
        user.ru_subscribed = True
    elif channel.language == 'en':
        user.en_subscribed = True
    elif channel.language == 'he':
        user.he_subscribed = True

    await objects.update(user, ['ru_subscribed', 'en_subscribed', 'he_subscribed'])
