from aiogram import Dispatcher

from .info import info, send_video


def setup(dp: Dispatcher) -> None:
    # Информация
    dp.register_callback_query_handler(info, lambda c: c.data == 'info')

    # Отправка видео
    dp.register_callback_query_handler(send_video, lambda c: c.data.startswith('get_video'))
