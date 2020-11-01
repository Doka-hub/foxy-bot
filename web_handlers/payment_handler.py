from aiohttp import web
from aiohttp.web_response import Response

import json

import logging

from models import objects, TGUser, Post

payment_handler_app = web.Application()
logging.basicConfig(filename='log.log', level=logging.INFO)


async def payment_handler(request: web.Request) -> web.Response:
    data = await request.post()
    invoice = data.get('invoice')
    return Response(body=json.dumps({'invoice': invoice}))


payment_handler_app.add_routes([web.post('/', payment_handler)])
