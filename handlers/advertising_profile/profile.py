from aiogram import types

from utils.db_api.user.language import get_language
from keyboards.inline.adversiting_profile.profile import get_advertising_profile_inline_keyboard

from data import config


# Рекламный профиль
async def advertising_profile(call_data: types.CallbackQuery) -> None:
    await call_data.message.delete()

    user_id = call_data.from_user.id
    user_language = await get_language(user_id)

    advertising_profile_inline_keyboard = await get_advertising_profile_inline_keyboard(user_language)
    text_answer = config.messages[user_language]['advertising_profile_name']
    await call_data.message.answer(text_answer, reply_markup=advertising_profile_inline_keyboard)
