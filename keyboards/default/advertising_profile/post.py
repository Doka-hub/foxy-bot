from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from data import config


def get_request_contact_default_keyboard(user_language: str) -> ReplyKeyboardMarkup:
    text_button = config.messages[user_language]['contact']['send_contact']
    get_contact_default_keyboard = ReplyKeyboardMarkup(
        [
            [
                KeyboardButton(
                    text_button, request_contact=True
                )
            ]
        ], one_time_keyboard=True
    )
    return get_contact_default_keyboard
