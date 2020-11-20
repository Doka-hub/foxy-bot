from aiogram import types


async def forward_handler(message: types.Message) -> None:
    await message.answer(str(message.forward_from_chat))
    await message.answer(str(message.forward_from_message_id))
