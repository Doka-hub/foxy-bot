from aiogram import bot as Bot
from aiogram import types
from aiogram.utils.exceptions import BadRequest

from models import objects, Channel

from .users import get_or_create_user


async def subscribe_user_to_channel(user_id: int, channel_id: int) -> None:
    user, created = await get_or_create_user(user_id)
    channel = await objects.get(Channel, channel_id=channel_id)

    if channel.language == 'ru':
        user.ru_subscribed = True
    elif channel.language == 'en':
        user.en_subscribed = True
    elif channel.language == 'he':
        user.he_subscribed = True

    await objects.update(user, ['ru_subscribed', 'en_subscribed', 'he_subscribed'])


async def check_user_subscribed(bot: Bot, channel_id: int, user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(channel_id, user_id)
        return True if member.status == 'member' else False
    except BadRequest:  # если участник не найден
        return False
