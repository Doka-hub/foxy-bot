from aiogram import types


async def get_message_id(message: types.Message) -> None:
    await message.answer(message.forward_from_message_id)
    await message.answer(message)
