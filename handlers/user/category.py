from aiogram import types
from aiogram.utils.exceptions import BadRequest

from keyboards.inline.category import get_check_subscribe_inline_keyboard, get_categories_inline_keyboard
from utils.db_api.channel import subscribe_user_to_channel
from utils.db_api.language import get_language
from utils.db_api.category import check_user_subscribe, get_channel_to_subscribe, subscribe_user_to_category

from data import config


# Выбор категории
async def choose_category(call_data: types.CallbackQuery) -> None:
    user_id = call_data.from_user.id
    user_language = await get_language(user_id)
    category_key = call_data.data.replace('choose_category ', '')  # example: 'choose_category health'

    if not await check_user_subscribe(user_id):
        await call_data.message.delete()

        channel_to_subscribe = await get_channel_to_subscribe(user_language)
        check_subscribe_inline_keyboard = get_check_subscribe_inline_keyboard(user_language, channel_to_subscribe)
        text_answer = config.messages[user_language]['subscribe_required']

        await call_data.message.answer(
            text_answer + channel_to_subscribe.channel_url,
            reply_markup=check_subscribe_inline_keyboard
        )
        return

    await subscribe_user_to_category(user_id, category_key)
    categories_inline_keyboard = await get_categories_inline_keyboard(user_id)
    await call_data.message.edit_reply_markup(reply_markup=categories_inline_keyboard)


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
