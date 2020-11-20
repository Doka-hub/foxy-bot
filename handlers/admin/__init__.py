from aiogram import Dispatcher

from .channel import register_channel


def setup(dp: Dispatcher) -> None:
    # channel
    dp.register_message_handler(register_channel, lambda m: m.forward_from_chat and m.text in ['ru', 'en', 'he'])
