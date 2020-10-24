from aiogram import Dispatcher
from aiogram.dispatcher.filters import CommandStart, CommandHelp

from .help import bot_help
from .start import start
from .language import choose_language, change_language
from .category import choose_category, check_subscribe


def setup(dp: Dispatcher):
    # start
    dp.register_message_handler(start, CommandStart())

    # help
    dp.register_message_handler(bot_help, CommandHelp())

    # language
    dp.register_callback_query_handler(choose_language, lambda c: c.data.startswith('choose_language'))
    dp.register_callback_query_handler(change_language, lambda c: c.data == 'change_language')

    # category
    dp.register_callback_query_handler(choose_category, lambda c: c.data.startswith('choose_category'))
    dp.register_callback_query_handler(check_subscribe, lambda c: c.data.startswith('check_subscribe'))

    # channel
