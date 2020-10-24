from typing import List

import ssl

import aiojobs as aiojobs
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.redis import RedisStorage2
from aiogram.types import ParseMode
from aiohttp import web
from loguru import logger

from data import config
from loader import bot, dp


# noinspection PyUnusedLocal
async def on_startup(app: web.Application):
    import middlewares
    import filters
    import handlers
    middlewares.setup(dp)
    filters.setup(dp)
    handlers.errors.setup(dp)
    handlers.user.setup(dp)
    logger.info('Configure Webhook URL to: {url}', url=config.WEBHOOK_URL)
    await bot.delete_webhook()
    await bot.set_webhook(config.WEBHOOK_URL, certificate=open('/home/admin/conf/web/ssl.getsub.cc.pem', 'r'))


async def on_shutdown(app: web.Application):
    app_bot: Bot = app['bot']
    await app_bot.close()


async def init() -> web.Application:
    from utils.misc import logging
    import web_handlers
    logging.setup()
    scheduler = await aiojobs.create_scheduler()

    app = web.Application(debug=True)
    subapps: List[str, web.Application] = [
        ('/health/', web_handlers.health_app),
        ('/tg/webhooks', web_handlers.tg_updates_app),
        ('/post/', web_handlers.post_app),
        ('/payment/handler/', web_handlers.payment_handler_app)
    ]
    for prefix, subapp in subapps:
        subapp['bot'] = bot
        subapp['dp'] = dp
        subapp['scheduler'] = scheduler
        app.add_subapp(prefix, subapp)
    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)
    return app


if __name__ == '__main__':
    # bot = Bot(config.BOT_TOKEN, parse_mode=ParseMode.HTML, validate_token=True)
    # storage = RedisStorage2(**config.redis)
    # dp = Dispatcher(bot,
                    # storage=storage
                    # )
    ssl_context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH, )
    web.run_app(init(), host='localhost', access_log=logger, backlog=2)
