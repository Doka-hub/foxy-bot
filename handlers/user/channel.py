from aiogram import types
from aiogram.utils.exceptions import BadRequest

from data import config
from keyboards.inline.user.category import get_categories_inline_keyboard

from utils.db_api.channel import subscribe_user_to_channel
from utils.db_api.language import get_language


# Проверить подписку
async def check_subscribe(call_data: types.CallbackQuery):
    user_id = call_data.from_user.id
    user_language = await get_language(user_id)
    channel_id = int(call_data.data.replace('check_subscribe ', ' '))

    try:
        await call_data.bot.get_chat_member(channel_id, user_id)
        await call_data.message.delete()
        await subscribe_user_to_channel(user_id)
    except BadRequest:
        return

    categories_inline_keyboard = await get_categories_inline_keyboard(user_id)
    text_answer = config.messages[user_language]['subscribe']

    await call_data.message.answer(
        text_answer,
        reply_markup=categories_inline_keyboard
    )


