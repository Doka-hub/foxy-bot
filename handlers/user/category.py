from aiogram import types

from data import config

from keyboards.inline.category import (
    get_check_subscribe_inline_keyboard, get_categories_inline_keyboard,
    get_time_to_mail_inline_keyboard
)

from utils.db_api.language import get_language
from utils.db_api.category import (
    check_user_subscribe, get_channel_to_subscribe, subscribe_user_to_category,
    set_user_time_to_mail
)


# Список категорий
async def category_list(call_data: types.CallbackQuery) -> None:
    await call_data.message.delete()

    user_id = call_data.from_user.id
    user_language = await get_language(user_id)

    categories_inline_keyboard = await get_categories_inline_keyboard(user_id)
    text_answer = config.messages[user_language]['subscribe']
    await call_data.message.answer(text_answer, reply_markup=categories_inline_keyboard)


# Подписка на категории
async def category_subscribe(call_data: types.CallbackQuery) -> None:
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


# Показать время рассылки
async def show_time_to_mail(call_data: types.CallbackQuery) -> None:
    await call_data.message.delete()

    user_id = call_data.from_user.id
    user_language = await get_language(user_id)

    time_to_mail_inline_keyboard = await get_time_to_mail_inline_keyboard(user_id)
    text_answer = config.messages[user_language]['time_to_mail_choose']
    await call_data.message.answer(text_answer, reply_markup=time_to_mail_inline_keyboard)


# Выбрать время для рассылки
async def choose_time_to_mail(call_data: types.CallbackQuery) -> None:
    time_to_mail = call_data.data.replace('choose_time_to_mail ', '')  # example: 'choose_time_to_mail morning'
    user_id = call_data.from_user.id

    time_to_mail_inline_keyboard = await get_time_to_mail_inline_keyboard(user_id)
    await set_user_time_to_mail(user_id, time_to_mail)
    await call_data.message.edit_reply_markup(
        reply_markup=time_to_mail_inline_keyboard
    )

