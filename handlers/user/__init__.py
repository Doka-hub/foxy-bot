from aiogram import Dispatcher
from aiogram.dispatcher.filters import CommandStart, CommandHelp, Command

from .help import bot_help
from .start import start
from .menu import menu
from .language import choose_language, change_language
from .category import category_subscribe, category_list, show_time_to_mail, choose_time_to_mail
from .channel import check_subscribe


def setup(dp: Dispatcher) -> None:
    # start
    dp.register_message_handler(start, CommandStart())

    # menu
    dp.register_message_handler(menu, Command(['menu']))
    dp.callback_query_handler(menu, lambda c: c.data == 'menu')

    # help
    dp.register_message_handler(bot_help, CommandHelp())

    # language
    dp.register_callback_query_handler(choose_language, lambda c: c.data.startswith('choose_language'))
    dp.register_callback_query_handler(change_language, lambda c: c.data == 'change_language')

    # category
    dp.register_callback_query_handler(category_list, lambda c: c.data == 'category_list')
    dp.register_callback_query_handler(category_subscribe, lambda c: c.data.startswith('choose_category'))
    dp.register_callback_query_handler(show_time_to_mail, lambda c: c.data == 'show_time_to_mail')
    dp.register_callback_query_handler(choose_time_to_mail, lambda c: c.data.startswith('choose_time_to_mail'))

    # channel
    dp.register_callback_query_handler(check_subscribe, lambda c: c.data.startswith('check_subscribe'))

