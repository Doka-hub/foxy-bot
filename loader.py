from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.redis import RedisStorage2
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import ParseMode

from data import config

bot = Bot(config.BOT_TOKEN, parse_mode=ParseMode.HTML, validate_token=True)
storage = RedisStorage2(**config.redis)
dp = Dispatcher(bot, storage=storage)
