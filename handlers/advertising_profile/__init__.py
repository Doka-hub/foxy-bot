from aiogram import Dispatcher, types

from states.adversiting_profile.post import PostState

from .profile import advertising_profile
from .post import (
    post_list, post_detail,
    post_create, get_contact, post_create_choose_channel_handle, post_create_choose_channel_hanlde_cancel,
    create_post_image, create_post_image_handle, create_post_image_handle_cancel
)


def setup(dp: Dispatcher) -> None:
    # profile
    dp.register_callback_query_handler(advertising_profile, lambda c: c.data == 'advertising_profile')

    # post
    dp.register_callback_query_handler(post_list, lambda c: c.data == 'post_list')
    dp.register_callback_query_handler(post_detail, lambda c: c.data.startswith('post_detail'))

    dp.register_callback_query_handler(post_create, lambda c: c.data == 'post_create')
    dp.register_message_handler(get_contact, content_types=['contact'])

    dp.register_callback_query_handler(post_create_choose_channel_handle, lambda c: c.data.startswith('choose_channel'),
                                       state=PostState.channel_id)
    dp.register_callback_query_handler(post_create_choose_channel_hanlde_cancel,
                                       lambda c: c.data == 'advertising_profile', state=PostState.channel_id)

    dp.register_callback_query_handler(create_post_image, lambda c: c.data == 'create_post_image')
    dp.register_message_handler(create_post_image_handle,
                                state=PostState.image_id, content_types=types.ContentTypes.PHOTO)
    dp.register_callback_query_handler(create_post_image_handle_cancel, lambda c: c.data == 'image_cancel',
                                       state=PostState.image_id)
