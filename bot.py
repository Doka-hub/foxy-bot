from typing import List

import ssl

import aiojobs as aiojobs
from aiogram import Bot
from aiohttp import web
from loguru import logger

from data import config
from loader import bot, dp


async def on_startup(app: web.Application):
    import middlewares
    import filters
    import handlers
    import models
    models.setup()
    middlewares.setup(dp)
    filters.setup(dp)
    handlers.errors.setup(dp)
    handlers.user.setup(dp)
    handlers.info.setup(dp)
    handlers.advertising_profile.setup(dp)
    handlers.admin.setup(dp)
    # logger.info('Configure Webhook URL to: {url}', url=config.WEBHOOK_URL)
    await bot.delete_webhook()
    await bot.set_webhook(config.WEBHOOK_URL)


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
        ('/tg/webhooks/', web_handlers.tg_updates_app),
        ('/post/', web_handlers.post_app),
        ('/payment/handler/', web_handlers.payment_handler_app),
        ('/payment-amount/', web_handlers.payment_amount_app)
    ]
    for prefix, subapp in subapps:
        subapp['bot'] = bot
        subapp['dp'] = dp
        subapp['scheduler'] = scheduler
        app.add_subapp(prefix, subapp)
    app['bot'] = bot
    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)
    return app


if __name__ == '__main__':
    # ssl_context = ssl.create_default_context(path='/home/admin/conf/web/ssl.getsub.cc.crt')
    # ssl_context.load_cert_chain('/home/admin/conf/web/ssl.getsub.cc.pem', '/home/admin/conf/web/ssl.getsub.cc.key')
    web.run_app(init(), host='localhost')
