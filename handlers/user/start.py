from aiogram import types

from utils.db_api.users import get_or_create_user
from keyboards.inline import get_language_inline_keyboard, get_menu_inline_keyboard

from data import config


async def start(message: types.Message) -> None:
    await message.bot.set_my_commands([types.BotCommand('menu', 'Show bot menu'), types.BotCommand('help', 'Help')])

    user_id = message.from_user.id
    username = message.from_user.username

    user, created = await get_or_create_user(user_id, username)
    user_language = user.language

    if not user_language:
        language_inline_keyboard = get_language_inline_keyboard()
        await message.answer('Выберите язык / Choose language / שפה נבחרתת', reply_markup=language_inline_keyboard)
        return

    menu_inline_keyboard = get_menu_inline_keyboard(user_language)
    text_answer = config.messages[user_language]['menu_name']
    await message.answer(text_answer, reply_markup=menu_inline_keyboard)
