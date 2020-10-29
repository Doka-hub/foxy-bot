from aiogram import types
from aiogram.utils.exceptions import BadRequest

from keyboards.inline.user.category import get_categories_inline_keyboard

from utils.db_api.channel import subscribe_user_to_channel
from utils.db_api.language import get_language

from data import config


# Проверить подписку
async def check_subscribe(call_data: types.CallbackQuery) -> None:
    user_id = call_data.from_user.id
    user_language = await get_language(user_id)
    channel_id = int(call_data.data.replace('check_subscribe ', ' '))

    try:
        member = await call_data.bot.get_chat_member(channel_id, user_id)
        if member.status == 'member':
            await call_data.message.delete()
            await subscribe_user_to_channel(user_id)
        else:
            text_answer = config.messages[user_language]['channel']['not_found']
            await call_data.answer(text_answer, show_alert=True)
            return
    except BadRequest:  # если участник не найден
        text_answer = config.messages[user_language]['channel']['not_found']
        await call_data.answer(text_answer, show_alert=True)
        return

    categories_inline_keyboard = await get_categories_inline_keyboard(user_id)
    text_answer = config.messages[user_language]['subscribe']
    await call_data.message.answer(text_answer, reply_markup=categories_inline_keyboard)


