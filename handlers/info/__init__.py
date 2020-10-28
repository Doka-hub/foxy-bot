from aiogram import Dispatcher

from .info import info


def setup(dp: Dispatcher) -> None:
    dp.register_callback_query_handler(info, lambda c: c.data == 'info')
