from aiogram import types


async def forward_handler(message: types.Message) -> None:
    await message.answer(type(message.forward_from_chat))
    await message.answer(message.forward_from_chat)
