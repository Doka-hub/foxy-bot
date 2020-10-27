from aiogram import types

from keyboards.inline.adversiting_profile.post import get_post_create_inline_keyboard, get_post_create_message

from utils.db_api.language import get_language

from loader import dp


async def post_create_detail(*, call_data: types.CallbackQuery = None, message: types.Message = None) -> None:
    """
    Функция отправляет форму для создания поста, подтягивая всю заполненную информацию.

    :param call_data: types.CallbackQuery
    :param message: types.Message
    :return: None
    """
    if call_data:
        user_id = call_data.from_user.id
        user_language = await get_language(user_id)

        post_data = await dp.storage.get_data(user=user_id)
        image_id = post_data.get('image_id')

        create_post_inline_keyboard = get_post_create_inline_keyboard(user_id, post_data)
        text_answer = get_post_create_message(user_language, post_data)

        # если картинка заполнена
        if image_id:
            await call_data.message.answer_photo(
                image_id,
                text_answer,
                reply_markup=create_post_inline_keyboard,
                parse_mode='markdown'
            )
        else:
            await call_data.message.answer(
                text_answer,
                reply_markup=create_post_inline_keyboard,
                parse_mode='markdown'
            )
    elif message:
        user_id = message.from_user.id
        user_language = await get_language(user_id=user_id)

        post_data = await dp.storage.get_data(user=user_id)
        image_id = post_data.get('image_id')

        create_post_inline_keyboard = get_post_create_inline_keyboard(user_id, post_data)
        text_answer = get_post_create_message(user_language, post_data)

        # если картинка заполнена
        if image_id:
            await message.answer_photo(
                image_id,
                text_answer,
                reply_markup=create_post_inline_keyboard,
                parse_mode='markdown'
            )
        else:
            await message.answer(
                text_answer,
                reply_markup=create_post_inline_keyboard,
                parse_mode='markdown'
            )
