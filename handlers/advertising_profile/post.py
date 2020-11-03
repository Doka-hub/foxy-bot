from aiogram import types
from aiogram.dispatcher import FSMContext

from models import objects, Post

from loader import dp

from states.adversiting_profile.post import PostState

from utils.db_api.user.language import get_language
from utils.db_api.user.user import get_or_create_user
from utils.db_api.adversiting_profile.post import (
    set_phone_number,
    save_post_data_and_get_payment_address, update_post_data
)
from utils.post.post_create_info import post_create_detail, check_post_must_fields_filled

from keyboards.inline.user.menu import get_menu_inline_keyboard
from keyboards.inline.adversiting_profile.profile import get_advertising_profile_inline_keyboard
from keyboards.inline.adversiting_profile.post import (
    get_post_list_inline_keyboard, get_post_detail_text_answer,

    get_post_inline_buttons, get_post_create_message, get_post_create_inline_keyboard,
    get_post_create_data_cancel_inline_keyboard, get_date_inline_keyboard, get_post_inline_button,

    get_post_moderate_answer_text, get_confirmation_text_answer, get_confirmation_inline_keyboard, get_pay_text_answer,

    get_choose_channel_to_mail_inline_keyboard
)
from keyboards.default.advertising_profile.post import get_request_contact_default_keyboard

from data import config

from .profile import advertising_profile


# Мои посты
async def post_list(call_data: types.CallbackQuery) -> None:
    await call_data.message.delete()

    user_id = call_data.from_user.id
    user_language = await get_language(user_id)

    post_create_inline_keyboard = await get_post_list_inline_keyboard(user_id)
    text_answer = config.messages[user_language]['advertising_profile']['post_list']
    await call_data.message.answer(text_answer, reply_markup=post_create_inline_keyboard)


# Детали поста
async def post_detail(call_data: types.CallbackQuery) -> None:
    await call_data.message.delete()

    user_id = call_data.from_user.id
    user_language = await get_language(user_id)

    post_id = call_data.data.replace('post_detail ', '')
    post = await objects.get(Post, id=post_id)

    message = await get_post_detail_text_answer(user_language, post)
    detail_post_inline_keyboard = get_post_inline_buttons(user_language, post)

    # если картинки нет
    if post.image_id != '0':
        await call_data.message.answer_photo(post.image_id, message, reply_markup=detail_post_inline_keyboard,
                                             parse_mode='markdown')
    else:
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


# Создать пост - обработка данных - отмена
async def post_create_handle_cancel(call_data: types.CallbackQuery, state: FSMContext) -> None:
    """
    Отменяет заполнение того или иного поля
    :param call_data:
    :param state:
    :return:
    """
    await call_data.message.delete()

    await state.reset_state(with_data=False)

    await post_create_detail(call_data=call_data)


# Создать пост - изображение
async def post_create_image(call_data: types.CallbackQuery) -> None:
    await call_data.message.delete()

    user_id = call_data.from_user.id
    user_language = await get_language(user_id)

    post_create_data_cancel_inline_keyboard = get_post_create_data_cancel_inline_keyboard(user_language)
    text_answer = config.messages[user_language]['post_create']['image_send']

    await call_data.message.answer(text_answer, reply_markup=post_create_data_cancel_inline_keyboard)
    await PostState.image_id.set()


# Создать пост - обработка изображения
async def post_create_image_handle(message: types.Message, state: FSMContext) -> None:
    photo_sizes = message.photo
    image_id = photo_sizes[-1].file_id  # [-1] - самый лучший размер

    await state.update_data(image_id=image_id)
    await state.reset_state(with_data=False)

    await post_create_detail(message=message)


# Создать пост - заголовок
async def post_create_title(call_data: types.CallbackQuery) -> None:
    await call_data.message.delete()

    user_id = call_data.from_user.id
    user_language = await get_language(user_id)

    post_create_data_cancel_inline_keyboard = get_post_create_data_cancel_inline_keyboard(user_language)
    text_answer = config.messages[user_language]['post_create']['title_send']

    await call_data.message.answer(text_answer, reply_markup=post_create_data_cancel_inline_keyboard)
    await PostState.title.set()


# Создать пост - обработка заголовка
async def post_create_title_handle(message: types.Message, state: FSMContext) -> None:
    await state.update_data(title=message.text)
    await state.reset_state(with_data=False)

    await post_create_detail(message=message)


# Создать пост - текст
async def post_create_text(call_data: types.CallbackQuery) -> None:
    await call_data.message.delete()

    user_id = call_data.from_user.id
    user_language = await get_language(user_id)

    post_create_data_cancel_inline_keyboard = get_post_create_data_cancel_inline_keyboard(user_language)
    text_answer = config.messages[user_language]['post_create']['text_send']

    await call_data.message.answer(text_answer, reply_markup=post_create_data_cancel_inline_keyboard)
    await PostState.text.set()


# Создать пост - обработка текста
async def post_create_text_handle(message: types.Message, state: FSMContext) -> None:
    await state.update_data(text=message.text)
    await state.reset_state(with_data=False)

    await post_create_detail(message=message)


# Создать пост - кнопка
async def post_create_button(call_data: types.CallbackQuery) -> None:
    await call_data.message.delete()

    user_id = call_data.from_user.id
    user_language = await get_language(user_id)

    post_create_data_cancel_inline_keyboard = get_post_create_data_cancel_inline_keyboard(user_language)
    text_answer = config.messages[user_language]['post_create']['button_format']

    await call_data.message.answer(text_answer, reply_markup=post_create_data_cancel_inline_keyboard,
                                   parse_mode='markdown',)
    await PostState.button.set()


# Создать пост - обработка кнопки
async def post_create_button_handle(message: types.Message, state: FSMContext) -> None:
    user_id = message.from_user.id
    user_language = await get_language(user_id)

    post_create_data_cancel_inline_keyboard = get_post_create_data_cancel_inline_keyboard(user_language)
    if ' - ' not in message.text:
        await message.bot.delete_message(message.chat.id, message.message_id - 1)

        text_answer = config.messages[user_language]['post_create']['button_invalid_format']
        await message.answer(text_answer, reply_markup=post_create_data_cancel_inline_keyboard, parse_mode='markdown')
        return

    url = message.text.split(' - ')[1]
    if not url.startswith('http://') and not url.startswith('https://'):
        await message.bot.delete_message(message.chat.id, message.message_id - 1)

        text_answer = config.messages[user_language]['post_create']['button_url_invalid_format']
        await message.answer(text_answer, reply_markup=post_create_data_cancel_inline_keyboard, parse_mode='markdown')
        return

    await state.update_data(button=message.text)
    await state.reset_state(with_data=False)

    await post_create_detail(message=message)


# Создать пост - выбор даты
async def post_create_date(call_data: types.CallbackQuery) -> None:
    await call_data.message.delete()

    user_id = call_data.from_user.id
    user_language = await get_language(user_id)
    post_data = await dp.storage.get_data(user=user_id)

    date_inline_keyboard = await get_date_inline_keyboard(user_language, post_data)
    text_answer = config.messages[user_language]['post_create']['date_choose']

    await call_data.message.answer(text_answer, reply_markup=date_inline_keyboard)
    await PostState.date.set()


# Создать пост - обработка даты
async def post_create_date_handle(call_data: types.CallbackQuery, state: FSMContext) -> None:
    await call_data.message.delete()

    date, time = call_data.data.replace('choose_date ', '').split('-')  # "date-time".split('-') => [date, time]
    await state.update_data(date=date, time=time)
    await state.reset_state(with_data=False)

    await post_create_detail(call_data=call_data)


# Создать пост - обработка даты - занято
async def post_create_handle_cancel_busy(call_data: types.CallbackQuery, state: FSMContext) -> None:
    user_id = call_data.from_user.id
    user_language = await get_language(user_id)

    text_answer = config.messages[user_language]['post_create']['date_busy']
    await call_data.answer(text_answer, show_alert=True)


# Создать пост - модерация
async def post_create_moderate(call_data: types.CallbackQuery) -> None:
    user_id = call_data.from_user.id
    user_language = await get_language(user_id)
    post_data = await dp.storage.get_data(user=user_id)

    is_must_field_filled, not_filled_field = check_post_must_fields_filled(post_data)
    if not is_must_field_filled:  # если обязательное поле не заполнено
        text_answer = config.messages[user_language]['post_create']['not_filled']
        field = config.messages[user_language]['must_fields']['field']
        state = config.messages[user_language]['must_fields'][not_filled_field]
        await call_data.answer(field + f' {state.lower()} ' + text_answer, show_alert=True)
        return

    await call_data.message.delete()

    image_id = post_data.get('image_id')
    text_answer = await get_post_moderate_answer_text(user_language, post_data)

    if image_id:
        mess = await call_data.message.answer_photo(image_id, text_answer, parse_mode='markdown')
    else:
        mess = await call_data.message.answer(text_answer, parse_mode='markdown')

    post_inline_button = await get_post_inline_button(post_data)
    if post_inline_button:
        await mess.edit_reply_markup(post_inline_button)

    confirmation_text_answer = get_confirmation_text_answer(user_language)
    confirmation_inline_keyboard = get_confirmation_inline_keyboard(user_language)
    await call_data.message.answer(confirmation_text_answer, reply_markup=confirmation_inline_keyboard)


# Создать пост - подтверждение (нет)
async def post_create_confirmation_decline(call_data: types.CallbackQuery) -> None:
    await call_data.message.delete()
    await post_detail(call_data=call_data)


# Создать пост - подтверждение (да)
async def post_create_confirmation_accept(call_data: types.CallbackQuery) -> None:
    await call_data.message.delete()

    user_id = call_data.from_user.id
    user_language = await get_language(user_id)

    post_data = await dp.storage.get_data(user=user_id)
    if post_data.get('edit'):
        await update_post_data(post_data)

        text_answer = config.messages[user_language]['post_update']['updated']
        await call_data.answer(text_answer, show_alert=True)
    else:
        payment_address = await save_post_data_and_get_payment_address(user_id, post_data)

        text_answer = await get_pay_text_answer(user_language, payment_address)
        await call_data.message.answer(text_answer, parse_mode='markdown')

    menu_inline_keyboard = get_menu_inline_keyboard(user_language)
    text_answer = config.messages[user_language]['menu_name']
    await call_data.message.answer(text_answer, reply_markup=menu_inline_keyboard, parse_mode='markdown')
    await dp.storage.reset_data(user=user_id)
