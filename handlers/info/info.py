from aiogram import types

from keyboards.inline.info import get_info_inline_keyboard

from utils.db_api.language import get_language

from data import config


# Информация
async def info(call_data: types.CallbackQuery) -> None:
    await call_data.message.delete()

    user_id = call_data.from_user.id
    user_language = await get_language(user_id)

    articles_inline_keyboard = await get_info_inline_keyboard(user_language)
    text_answer = config.messages[user_language]['menu']['info']

    await call_data.message.answer(text_answer, reply_markup=articles_inline_keyboard)
