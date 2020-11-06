from typing import Optional

from aiogram.utils.exceptions import BadRequest

from models import objects, Channel

from .language import get_language

from loader import bot

from data import config


async def get_channel(language: Optional[str] = None, channel_id: Optional[int] = None) -> Channel:
    if language:
        channel = await objects.get(Channel, language=language)
    else:
        channel = await objects.get(Channel, channel_id=channel_id)
    return channel


async def check_user_channel_subscribed(user_id: int, channel_id: Optional[int] = None) -> bool:
    if user_id in config.ADMINS.values():
        return True

    if not channel_id:
        user_language = await get_language(user_id)
        channel = await get_channel(user_language)
        channel_id = channel.channel_id

    try:
        member = await bot.get_chat_member(channel_id, user_id)
        return True if member.status == 'member' else False
    except BadRequest:  # если участник не найден
        return False
