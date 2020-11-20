from aiogram import types

from models import objects, Channel

from data import config


# Регистрация канала для постинга
async def register_channel(message: types.Message):
    channel = message.forward_from_chat
    channel_language = message.text
    channel_title = channel.title
    channel_id = channel.id
    channel_url = await channel.export_invite_link()

    admins = [member.user.username for member in await message.bot.get_chat_administrators(channel_id)]
    if config.BOT_USERNAME in admins:
        await objects.get_or_create(
            Channel,
            channel_id=channel_id,
            channel_url=channel_url,
            channel_title=channel_title,
            language=channel_language,
        )
        await message.answer(f'Канал {channel.title} добавлен')
