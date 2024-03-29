from aiogram import types

from keyboards.inline.user.category import get_categories_inline_keyboard

from utils.db_api.user.channel import check_user_channel_subscribed
from utils.db_api.user.language import get_language

from data import config


# Проверить подписку
async def check_subscribe(call_data: types.CallbackQuery) -> None:
    user_id = call_data.from_user.id
    user_language = await get_language(user_id)

    channel_id = int(call_data.data.replace('check_subscribe ', ' '))
    user_subscribed = await check_user_channel_subscribed(user_id, channel_id)

    if not user_subscribed:
        text_answer = config.messages[user_language]['channel']['not_found']
        await call_data.answer(text_answer, show_alert=True)
        return
    await call_data.message.delete()

    categories_inline_keyboard = await get_categories_inline_keyboard(user_id)
    text_answer = config.messages[user_language]['subscribe']
    await call_data.message.answer(text_answer, reply_markup=categories_inline_keyboard)



