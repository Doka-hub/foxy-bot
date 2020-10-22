from aiogram import Dispatcher
from aiogram.dispatcher.filters import CommandStart, CommandHelp

from .help import bot_help
from .start import start
from .language import choose_language


def setup(dp: Dispatcher):
    dp.register_message_handler(start, CommandStart())
    dp.register_message_handler(bot_help, CommandHelp())
    dp.register_message_handler(choose_language, lambda c: c.data.startswith('choose_language'))
