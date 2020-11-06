from aiogram import types

from typing import Dict, Union, List

from keyboards.inline.adversiting_profile.post import get_post_create_inline_keyboard, get_post_create_message

from utils.db_api.user.language import get_language

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

        post_create_inline_keyboard = get_post_create_inline_keyboard(user_language, post_data)
        text_answer = get_post_create_message(user_language, post_data)

        # если картинка заполнена
        if image_id != '0':
            await call_data.message.answer_photo(image_id, text_answer, reply_markup=post_create_inline_keyboard,
                                                 parse_mode='markdown')
        else:
            await call_data.message.answer(text_answer, reply_markup=post_create_inline_keyboard, parse_mode='markdown')
    elif message:
        user_id = message.from_user.id
        user_language = await get_language(user_id=user_id)

        post_data = await dp.storage.get_data(user=user_id)
        image_id = post_data.get('image_id')

        post_create_inline_keyboard = get_post_create_inline_keyboard(user_language, post_data)
        text_answer = get_post_create_message(user_language, post_data)

        # если картинка заполнена
        if image_id != '0':
            await message.answer_photo(image_id, text_answer, reply_markup=post_create_inline_keyboard,
                                       parse_mode='markdown')
        else:
            await message.answer(text_answer, reply_markup=post_create_inline_keyboard, parse_mode='markdown')


def check_post_must_fields_filled(post_data: Dict) -> List[Union[bool, str]]:
    """
    :param post_data:
    :return: возвращает список из двух значений. Первое - заполнены ли обязательные поля, второе какие поля не заполнены
    """
    if 'date' in post_data:
        if 'image_id' in post_data:
            return [True, None]
        elif 'text' in post_data:
            return [True, None]
        return [False, 'image_or_text']
    return [False, 'date']
