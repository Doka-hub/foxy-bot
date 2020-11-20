from aiogram import types


async def forward_handler(message: types.Message) -> None:
    from_chat_id = str(message.forward_from_chat.id)
    message_id = str(message.forward_from_message_id)
    await message.answer(str(from_chat_id) + ' ' + str(message_id))

