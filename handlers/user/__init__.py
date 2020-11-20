from aiogram import Dispatcher
from aiogram.dispatcher.filters import CommandStart, Command

from .start import start
from .menu import menu, back_to_menu
from .language import choose_language, change_language
from .category import category_subscribe, category_list, show_time_to_mail, choose_time_to_mail
from .channel import check_subscribe
from .forward import forward_handler


def setup(dp: Dispatcher) -> None:
    # forward
    dp.register_message_handler(forward_handler, lambda m: m.forward_from_chat and m.text not in ['ru', 'en', 'he'])

    # start
    dp.register_message_handler(start, CommandStart())

    # menu
    dp.register_message_handler(menu, Command(['menu']))
    dp.register_callback_query_handler(back_to_menu, lambda c: c.data == 'menu')

    # language
    dp.register_callback_query_handler(choose_language, lambda c: c.data.startswith('choose_language'))
    dp.register_callback_query_handler(change_language, lambda c: c.data == 'change_language')

    # category
    dp.register_callback_query_handler(category_list, lambda c: c.data == 'category_list')
    dp.register_callback_query_handler(category_subscribe, lambda c: c.data.startswith('choose_category'))
    # category - time_to_mail
    dp.register_callback_query_handler(show_time_to_mail, lambda c: c.data == 'show_time_to_mail')
    dp.register_callback_query_handler(choose_time_to_mail, lambda c: c.data.startswith('choose_time_to_mail'))

    # channel
    dp.register_callback_query_handler(check_subscribe, lambda c: c.data.startswith('check_subscribe'))

