from aiohttp import web

import json

import logging

from models import objects, TGUser, Post

payment_handler_app = web.Application()
logging.basicConfig(filename='log.log', level=logging.INFO)


async def payment_handler(request: web.Request) -> str:
    data = json.dumps(await request.post())
    invoice = data.get('invoice')
    print(data)
    return invoice


payment_handler_app.add_routes([web.post('/', payment_handler)])
