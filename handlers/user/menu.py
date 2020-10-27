from aiogram import types

from utils.db_api.users import get_or_create_user

from keyboards.inline.user.menu import get_menu_inline_keyboard
from keyboards.inline.user.language import get_language_inline_keyboard

from data import config
from data import messages


# Меню
async def menu(message: types.Message) -> None:
    user_id = message.from_user.id
    username = message.from_user.username

    user, created = await get_or_create_user(user_id, username)
    user_language = user.language

    if not user_language:
        language_inline_keyboard = get_language_inline_keyboard()
        await message.answer('Выберите язык / Choose language / שפה נבחרתת', reply_markup=language_inline_keyboard)
        return

    menu_inline_keyboard = get_menu_inline_keyboard(user_language)
    # text_answer = config.messages[user_language]['menu_name']
    text_answer = messages['hello']
    await message.answer(text_answer, reply_markup=menu_inline_keyboard)


# Меню (возвращение)
async def back_to_menu(call_data: types.CallbackQuery) -> None:
    await call_data.message.delete()

    user_id = call_data.from_user.id
    username = call_data.message.from_user.username

    user, created = await get_or_create_user(user_id, username)
    user_language = user.language

    if not user_language:
        language_inline_keyboard = get_language_inline_keyboard()
        await call_data.message.answer('Выберите язык / Choose language / שפה נבחרתת', reply_markup=language_inline_keyboard)
        return

    menu_inline_keyboard = get_menu_inline_keyboard(user_language)
    text_answer = config.messages[user_language]['menu_name']
    await call_data.message.answer(text_answer, reply_markup=menu_inline_keyboard)
