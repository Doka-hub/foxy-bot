from aiogram import Bot, Dispatcher, types
from aiohttp import web

tg_updates_app = web.Application()


async def proceed_update(request: web.Request):
    updates = [types.Update(**(await request.json()))]
    Bot.set_current(request.app['bot'])
    Dispatcher.set_current(request.app['dp'])
    await request.app['dp'].process_updates(updates)


async def execute(request: web.Request) -> web.Response:
    await request.app['scheduler'].spawn(proceed_update(req))
    return web.Response()


tg_updates_app.add_routes([web.post('/{token}', execute)])
