from aiogram import Dispatcher

from states.adversiting_profile.post import PostState

from .profile import advertising_profile
from .post import (
    post_list, post_detail, post_create, get_contact, post_create_choose_channel, post_create_choose_channel_cancel
)


def setup(dp: Dispatcher) -> None:
    # advertising_profile
    dp.callback_query_handler(advertising_profile, lambda c: c.data == 'advertising_profile')
    dp.callback_query_handler(post_list, lambda c: c.data == 'post_list')
    dp.callback_query_handler(post_detail, lambda c: c.startswith('post_detail'))
    dp.callback_query_handler(post_create, lambda c: c.data == 'post_create')
    dp.message_handler(get_contact, content_types=['contact'])
    dp.callback_query_handler(post_create_choose_channel, lambda c: c.data.startswith('choose_channel'),
                              state=PostState.channel_id)
    dp.callback_query_handler(post_create_choose_channel_cancel, lambda c: c.data == 'advertising_profile',
                              state=PostState.channel_id)
