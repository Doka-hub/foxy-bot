from aiogram import types
from aiogram.dispatcher import FSMContext

from models import objects, Post

from loader import dp

from states.adversiting_profile.post import PostState

from utils.db_api.language import get_language
from utils.db_api.users import get_or_create_user
from utils.db_api.adversiting_profile.post import set_phone_number

from keyboards.inline.adversiting_profile.profile import get_advertising_profile_inline_keyboard
from keyboards.inline.adversiting_profile.post import (
    get_list_post_inline_keyboard, get_post_detail_text_answer, get_post_inline_buttons,
    get_choose_channel_to_mail_inline_keyboard, get_post_create_message, get_post_create_inline_keyboard
)
from keyboards.default.advertising_profile.post import get_request_contact_default_keyboard

from data import config

from .profile import advertising_profile


# Мои посты
async def post_list(call_data: types.CallbackQuery) -> None:
    await call_data.message.delete()

    user_id = call_data.from_user.id
    user_language = await get_language(user_id)

    create_post_inline_keyboard = await get_list_post_inline_keyboard(user_id)
    text_answer = config.messages[user_language]['advertising_profile']['my_posts']
    await call_data.message.answer(text_answer, reply_markup=create_post_inline_keyboard)


# Детали поста
async def post_detail(call_data: types.CallbackQuery) -> None:
    await call_data.message.delete()

    user_id = call_data.from_user.id
    user_language = await get_language(user_id)

    post_id = call_data.data.replace('post_detail ', '')
    post = await objects.get(Post, id=post_id)

    message = get_post_detail_text_answer(user_language, post)
    detail_post_inline_keyboard = get_post_inline_buttons(user_language, post)

    # если картинки нет
    if post.image_id != '0':
        await call_data.message.answer_photo(
            post.image_id, message, reply_markup=detail_post_inline_keyboard, parse_mode='markdown'
        )
        return
    await call_data.message.answer(message, reply_markup=detail_post_inline_keyboard, parse_mode='markdown')


# Создать пост
async def post_create(call_data: types.CallbackQuery) -> None:
    await call_data.message.delete()

    user_id = call_data.from_user.id
    user, created = await get_or_create_user(user_id)
    user_language = user.language

    # запрашиваем номер телефона
    if not user.phone_number:
        request_contact_default_keyboard = get_request_contact_default_keyboard(user_language)
        text_answer = config.messages[user_language]['contact']['request_contact']
        await call_data.message.answer(text_answer, reply_markup=request_contact_default_keyboard)
        return

    choose_channel_to_mail_inline_keyboard = await get_choose_channel_to_mail_inline_keyboard(user_language)
    text_answer = config.messages[user_language]['channel']['choose_channel']
    await call_data.message.answer(text_answer, reply_markup=choose_channel_to_mail_inline_keyboard)
    await PostState.channel_id.set()


# Обработка контакта
async def get_contact(message: types.Message) -> None:
    wait_message = await message.answer('...', reply_markup=types.ReplyKeyboardRemove())
    await wait_message.delete()

    user_id = message.from_user.id
    user_language = await get_language(user_id)
    user_phone_number = message.contact['phone_number']
    await set_phone_number(user_id, user_phone_number)

    advertising_profile_inline_keyboard = await get_advertising_profile_inline_keyboard(user_language)
    text_answer = config.messages[user_language]['advertising_profile_name']
    await message.answer(text_answer, reply_markup=advertising_profile_inline_keyboard)


# Создать пост - выбора канал
async def post_create_choose_channel(call_data: types.CallbackQuery, state: FSMContext) -> None:
    await call_data.message.delete()

    channel_id = call_data.data.replace('choose_channel ', '')  # example: 'choose_channel 1'
    await state.update_data(channel_id=channel_id)
    await state.reset_state(with_data=False)

    user_id = call_data.from_user.id
    user_language = await get_language(user_id)
    post_data = await state.get_data()

    post_create_inline_keyboard = get_post_create_inline_keyboard(user_language, post_data)
    text_answer = get_post_create_message(user_language, post_data)
    await call_data.message.answer(text_answer, reply_markup=post_create_inline_keyboard)


# Создать пост - выбора канал - отмена
async def post_create_choose_channel_cancel(call_data: types.CallbackQuery, state: FSMContext) -> None:
    await state.reset_state()
    await advertising_profile(call_data)


# Рекламный профиль - отмена
async def post_create_cancel(call_data: types.CallbackQuery) -> None:
    user_id = call_data.from_user.id
    await dp.storage.reset_data(user=user_id)
    await advertising_profile(call_data)

