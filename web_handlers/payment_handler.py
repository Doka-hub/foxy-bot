from aiohttp import web

import json

import logging

from models import objects, TGUser, Post

payment_handler_app = web.Application()
logging.basicConfig(filename='log.log', level=logging.INFO)


async def payment_handler(request: web.Request) -> str:
    logging.info('%s' % await request.text() + '%s' % request.content)
    print(await request.text())
    # print(await request.json())
    print(request.content)
    data = json.dumps(await request.json())
    invoice = data.get('invoice')
    print(data)
    return invoice


payment_handler_app.add_routes([web.post('/', payment_handler)])
