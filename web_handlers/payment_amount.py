from aiohttp import web

import aiohttp_jinja2
import jinja2

import logging

from models import objects, PaymentAmount


payment_amount_app = web.Application()
aiohttp_jinja2.setup(payment_amount_app, loader=jinja2.FileSystemLoader('templates'))


@aiohttp_jinja2.template('payment_amount/payment_amount-detail.html')
async def get_payment_amount_detail(request: web.Request) -> dict:
    response = {}
    payment_amount = await objects.get(PaymentAmount)

    response['payment_amount'] = payment_amount
    return response


@aiohttp_jinja2.template('payment_amount/payment_amount-detail.html')
async def post_payment_amount_detail(request: web.Request) -> dict:
    post_data = await request.post()
    payment_amount = await objects.get(PaymentAmount)
    payment_amount.amount = post_data.get('payment_amount')
    await objects.update(payment_amount, ['amount'])

    return await get_payment_amount_detail(request)


payment_amount_app.add_routes(
    [
        web.get('/', get_payment_amount_detail),
        web.post('/', post_payment_amount_detail)
    ]
)
