from aiogram import types

from utils.db_api.users import set_language
from keyboards.inline import get_menu_inline_keyboard

from data import config


async def choose_language(call_data: types.CallbackQuery):
    await call_data.message.delete()

    user_id = call_data.from_user.id
    user_language = call_data.data[-2:]

    await set_language(user_id, user_language)

    menu_inline_keyboard = get_menu_inline_keyboard(user_language)
    text_answer = config.messages[user_language]['menu_name']

    await call_data.message.answer(text_answer, reply_markup=menu_inline_keyboard)
