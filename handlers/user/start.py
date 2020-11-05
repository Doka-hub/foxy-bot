from aiogram import types

from .menu import menu


# Старт
async def start(message: types.Message) -> None:
    await message.bot.set_my_commands([types.BotCommand('menu', 'show bot menu')])
    await menu(message)
