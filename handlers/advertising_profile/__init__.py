from aiogram import Dispatcher, types

from states.adversiting_profile.post import PostState

from .profile import advertising_profile
from .post import (
    post_list, post_detail,


    post_create, post_create_cancel, get_contact, post_create_choose_channel_handle,
    post_create_choose_channel_handle_cancel,
    post_create_image, post_create_image_handle,

    post_create_title, post_create_title_handle,

    post_create_text, post_create_text_handle,

    post_create_button, post_create_button_handle,

    post_create_date, post_create_date_handle, post_create_handle_cancel_busy,

    post_create_moderate, post_create_confirmation_decline, post_create_confirmation_accept,

    post_create_handle_cancel,

    post_update
)


def setup(dp: Dispatcher) -> None:
    # profile
    dp.register_callback_query_handler(advertising_profile, lambda c: c.data == 'advertising_profile')

    # post
    dp.register_callback_query_handler(post_list, lambda c: c.data == 'post_list')
    dp.register_callback_query_handler(post_detail, lambda c: c.data.startswith('post_detail'))

    # Создание поста
    dp.register_callback_query_handler(post_create, lambda c: c.data == 'post_create')
    dp.register_callback_query_handler(post_create_cancel, lambda c: c.data == 'post_cancel')
    dp.register_message_handler(get_contact, content_types=['contact'])

    # Изменение поста
    dp.register_callback_query_handler(post_update, lambda c: c.data.startswith('post_update'))

    # Создание поста - канал
    dp.register_callback_query_handler(post_create_choose_channel_handle, lambda c: c.data.startswith('choose_channel'),
                                       state=PostState.channel_id)
    dp.register_callback_query_handler(post_create_choose_channel_handle_cancel,
                                       lambda c: c.data == 'advertising_profile', state=PostState.channel_id)

    # Создание поста - картинка
    dp.register_callback_query_handler(post_create_image, lambda c: c.data == 'post_create_image')
    dp.register_callback_query_handler(post_create_image, lambda c: c.data == 'post_update_image')
    dp.register_message_handler(post_create_image_handle,
                                state=PostState.image_id, content_types=types.ContentTypes.PHOTO)
    dp.register_callback_query_handler(post_create_handle_cancel, lambda c: c.data == 'data_cancel',
                                       state=PostState.image_id)

    # Создание поста - заголовок
    dp.register_callback_query_handler(post_create_title, lambda c: c.data == 'post_create_title')
    dp.register_callback_query_handler(post_create_title, lambda c: c.data == 'post_update_title')
    dp.register_message_handler(post_create_title_handle,
                                state=PostState.title, content_types=types.ContentTypes.TEXT)
    dp.register_callback_query_handler(post_create_handle_cancel, lambda c: c.data == 'data_cancel',
                                       state=PostState.title)

    # Создание поста - текст
    dp.register_callback_query_handler(post_create_text, lambda c: c.data == 'post_create_text')
    dp.register_callback_query_handler(post_create_text, lambda c: c.data == 'post_update_text')
    dp.register_message_handler(post_create_text_handle,
                                state=PostState.text, content_types=types.ContentTypes.TEXT)
    dp.register_callback_query_handler(post_create_handle_cancel, lambda c: c.data == 'data_cancel',
                                       state=PostState.text)

    # Создание поста - кнопка
    dp.register_callback_query_handler(post_create_button, lambda c: c.data == 'post_create_button')
    dp.register_callback_query_handler(post_create_button, lambda c: c.data == 'post_update_button')
    dp.register_message_handler(post_create_button_handle,
                                state=PostState.button, content_types=types.ContentTypes.TEXT)
    dp.register_callback_query_handler(post_create_handle_cancel, lambda c: c.data == 'data_cancel',
                                       state=PostState.button)

    # Создание поста - дата
    dp.register_callback_query_handler(post_create_date, lambda c: c.data == 'post_create_date')
    dp.register_callback_query_handler(post_create_date, lambda c: c.data == 'post_update_date')
    dp.register_callback_query_handler(post_create_date_handle,
                                       lambda c: c.data.startswith('choose_date'), state=PostState.date)
    dp.register_callback_query_handler(post_create_handle_cancel, lambda c: c.data == 'data_cancel',
                                       state=PostState.date)
    dp.register_callback_query_handler(post_create_handle_cancel_busy, lambda c: c.data == 'date_busy',
                                       state=PostState.date)

    # Создание поста - модерация
    dp.register_callback_query_handler(post_create_moderate, lambda c: c.data == 'post_moderate')
    dp.register_callback_query_handler(post_create_confirmation_decline, lambda c: c.data == 'confirmation_decline')
    dp.register_callback_query_handler(post_create_confirmation_accept, lambda c: c.data == 'confirmation_accept')
