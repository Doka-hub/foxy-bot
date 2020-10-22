from aiohttp import web


from models import objects, User, Post


payment_handler_app = web.Application()


async def payment_handler(request: web.Request):
    data = await request.json()
    invoice = data.get('invoice')
    return invoice


payment_handler_app.add_routes([web.post('/', payment_handler)])
