from aiohttp import web
from aiohttp.web_response import Response

import json

import logging

from models import objects, Post, PaymentAddress, TGUser

from loader import bot

payment_handler_app = web.Application()
logging.basicConfig(filename='log.log', level=logging.INFO)

'''
data:

event=unconfirmed&address=2N3B6SesF31QQT7EeS9Thxu8UqHanDWyURQ
&tx_hash=de06ead3bb22385ba5ba227b9d4c50123954a17408d8b04365822ccbc4c0dd9b
&tx_out=0&code=PMTv65sHYBZnrHLKSzRV9mLRzZwxCRQ8evB2XTvabm312KbsuU1Eg
&invoice=invP9mRZGjYkweWx6DwsJQmciZQfFgDCyCTPzo4FhsLGouqTjVYSw&confirmations=0
&received_amount=0&pending_received_amount=450000&pending_received_tx=6
&received_tx=0&amount=75000&signature=1523d859c4682bf724a3ec996f10e9c64289dd108f4b067ecd5ac05c2f461a00
&currency=tBTC&BTCUSD_HITBTC=13826.73&BTCUSD_BITTREX=13834.76&BTCUSD_BITFINEX=13833.0
&BTCUSD_BITSTAMP=13831.85&BTCUSD_COINBASEPRO=13839.63&BTCUSD_KRAKEN=13837.1
&BTCUSD_GEMINI=13838.89&BTCUSD_AVERAGE=13830.91
'''


async def payment_handler(request: web.Request) -> Response:
    data = await request.post()
    invoice = data.get('invoice')

    address = data.get('address')
    amount = int(data.get('amount'))
    payment_address = await objects.get(PaymentAddress, address=address)

    if amount >= payment_address.amount:
        post = payment_address.post.get()
        post.status = 'processing'
        post.paid = True

        user_id = post.user.user_id

        await objects.update(post, ['status', 'paid'])
        await bot.send_message(user_id, f'{post.status}')

    return Response(body=json.dumps({'invoice': invoice}))


payment_handler_app.add_routes([web.post('/', payment_handler)])
