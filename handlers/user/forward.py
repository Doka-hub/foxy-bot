from aiogram import types

from loader import bot


async def forward_handler(message: types.Message) -> None:
    from_chat_id = str(message.forward_from_chat.id)
    message_id = str(message.forward_from_message_id)
    await bot.forward_message(message.chat.id, from_chat_id, message_id)
