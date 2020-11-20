from aiogram import types
from aiogram.types.message import Message
from aiogram.types.message_entity import MessageEntity

from loader import bot


async def get_message_id(message: types.Message) -> None:
    message_id = message.forward_from_message_id
    from_chat_id = message.migrate_from_chat_id
    await bot.forward_message(message.chat.id, from_chat_id, message_id)
