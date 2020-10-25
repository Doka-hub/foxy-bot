from aiogram import Dispatcher

from .channel import register_channel


def setup(dp: Dispatcher):
    # channel
    dp.register_message_handler(register_channel, lambda m: m.forward_from_chat)
