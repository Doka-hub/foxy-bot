from aiohttp import web
import json

from models import objects, TGUser, Post


payment_handler_app = web.Application()


async def payment_handler(request: web.Request) -> str:
    data = json.dumps(await request.json())
    invoice = data.get('invoice')
    print(data)
    return invoice


payment_handler_app.add_routes([web.post('/', payment_handler)])
