from aiogram import types

from models import objects, Channel


# Регистрация канала для постинга
async def register_channel(message: types.Message):
    channel = message.forward_from_chat
    channel_language = message.text
    channel_title = channel.title
    channel_id = channel.id
    channel_url = await channel.export_invite_link()

    if channel_language not in ['ru', 'en', 'he']:
        await message.answer('ru, en, he')
        return

    admins = [member.user.username for member in await message.bot.get_chat_administrators(channel_id)]
    if 'foxy3bot' in admins:
        await objects.get_or_create(
            Channel,
            channel_id=channel_id,
            channel_url=channel_url,
            channel_title=channel_title,
            language=channel_language,
        )
        await message.answer(f'Канал {channel.title} добавлен')
