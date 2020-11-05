from decimal import Decimal, ROUND_CEILING

import logging

import json

from aiohttp import ClientSession
from aiohttp.web_response import Response

from models import objects, PaymentAmount


logging.basicConfig(filename='bot_logs/payment.log', level=logging.INFO)


async def get_ad_cost() -> Decimal:
    """
    :return: стоимость рекламного поста в биткоинах
    """
    url = 'https://api.bitaps.com/market/v1/ticker/btcusd'
    async with ClientSession() as session:
        response = await session.get(url)

        usd = (await objects.get(PaymentAmount)).amount  # стоимость рекламного поста. см /payment-amount/
        usdbtc = Decimal((await response.json())['data']['open'])  # актуальный курс биткоина в долларах
        btc = usd / Decimal(usdbtc)  # стоимость рекламного поста в btc
    return btc.quantize(Decimal('1.00000'),
                        ROUND_CEILING)  # ROUND_CEILING - округляет число в большую сторону


async def create_payment_address(forwarding_address: str, callback_link: str) -> Response:
    """
    :param forwarding_address: адрес куда будут пересылатсья деньги
    :param callback_link: ссылка для уведомлений о платежах
    :return: данные о созданном адресе
    """
    url = 'https://api.bitaps.com/btc/v1/create/payment/address'
    data = json.dumps({'forwarding_address': forwarding_address, 'callback_link': callback_link})

    async with ClientSession() as client:
        response = await client.post(url, data=data)
        return await response.json()
