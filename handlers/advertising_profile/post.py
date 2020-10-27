from aiogram import types
from aiogram.dispatcher import FSMContext

from models import objects, Post

from loader import dp

from states.adversiting_profile.post import PostState

from utils.keyboards.inline import get_inline_keyboard
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


# Создать пост - отмена
async def post_create_cancel(call_data: types.CallbackQuery) -> None:
    user_id = call_data.from_user.id
    await dp.storage.reset_data(user=user_id)
    await advertising_profile(call_data)


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


# Создать пост - обработка выбора канала
async def post_create_choose_channel_handle(call_data: types.CallbackQuery, state: FSMContext) -> None:
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


# Создать пост - обработка выбора канала - отмена
async def post_create_choose_channel_hanlde_cancel(call_data: types.CallbackQuery, state: FSMContext) -> None:
    await state.reset_state()
    await advertising_profile(call_data)


# Создать пост - изображение
async def create_post_image(call_data: types.CallbackQuery) -> None:
    await call_data.message.delete()

    user_id = call_data.from_user.id
    user_language = await get_language(user_id)

    image_cancel_inline_keyboard = get_inline_keyboard(
        [[types.InlineKeyboardButton(config.messages[user_language]['cancel'], callback_data='image_cancel')]]
    )
    text_answer = config.messages[user_language]['create_post']['image_send']
    await call_data.message.answer(text_answer, reply_markup=image_cancel_inline_keyboard)
    await Post.image_id.set()


# Создать пост - обработка изображения
async def create_post_image_handle(message: types.Message, state: FSMContext) -> None:
    photo_sizes = message.photo
    image_id = photo_sizes[-1].file_id  # [-1] - самый лучший размер

    await state.update_data(image_id=image_id)
    await state.reset_state(with_data=False)

    user_id = message.from_user.id
    post_data = await dp.storage.get_data(user=user_id)

    create_post_inline_keyboard = get_post_create_inline_keyboard(user_id, post_data)
    await message.answer_photo(
        image_id,
        create_post_inline_keyboard[1],
        reply_markup=create_post_inline_keyboard[0],
        parse_mode='markdown'
    )


# Создать пост - обработка изображения - отмена
async def create_post_image_handle_cancel(call_data: types.CallbackQuery, state: FSMContext):
    await call_data.message.delete()
    await state.reset_state(with_data=False)

    user_id = call_data.from_user.id
    user_language = await get_language(user_id)
    post_data = await dp.storage.get_data(user=user_id)
    image_id = post_data.get('image_id')

    create_post_inline_keyboard = get_post_create_inline_keyboard(user_id, post_data)
    text_answer = get_post_create_message(user_language, post_data)
    if image_id:
        await call_data.message.answer_photo(
            image_id,
            create_post_inline_keyboard[1],
            reply_markup=create_post_inline_keyboard[0],
            parse_mode='markdown'
        )
    else:
        await call_data.message.answer(
            create_post_inline_keyboard[1],
            reply_markup=create_post_inline_keyboard[0],
            parse_mode='markdown'
        )
