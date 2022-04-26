from aiogram import types

from utils.db_api.user.language import set_language
from utils.db_api.user import get_or_create_user

from keyboards.inline.user.menu import get_menu_inline_keyboard
from keyboards.inline.user.language import get_language_inline_keyboard

from data import config


# Выбор языка
async def choose_language(call_data: types.CallbackQuery) -> None:
    await call_data.message.delete()

    user_id = call_data.from_user.id
    user, created = await get_or_create_user(user_id)
    user_language = call_data.data[-2:]  # последние два символа это язык ('choose_language ru')

    print(user_id, user_language)

    # if not user.language:
    #     pinned_message = config.messages[user_language]['pinned']
    #     from_chat_id = pinned_message['from_chat_id']
    #     message_id = pinned_message['message_id']
    #     await call_data.bot.forward_message(call_data.message.chat.id, from_chat_id, message_id)

    print(2)

    menu_inline_keyboard = get_menu_inline_keyboard(user_language)
    text_answer = config.messages[user_language]['menu_name']
    await call_data.message.answer(text_answer, reply_markup=menu_inline_keyboard)
    await set_language(user_id, user_language)


# Смена языка
async def change_language(call_data: types.CallbackQuery) -> None:
    await call_data.message.delete()

    language_inline_keyboard = get_language_inline_keyboard()
    await call_data.message.answer('Выберите язык / Choose language / בחר שפה', reply_markup=language_inline_keyboard)
