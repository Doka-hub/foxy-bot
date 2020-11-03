from typing import Union, List

import json

from time import time

from aiohttp import ClientSession
from aiohttp.web_response import Response

from hashlib import sha256
from hmac import new as hmac_new, HMAC


def create_nonce_and_hmac_signature(wallet_id: str, password: str) -> List[Union[str, HMAC]]:
    nonce = str(int(time() * 1000))
    key = sha256(sha256((wallet_id + password).encode()).digest()).digest()
    msg = wallet_id + nonce
    signature = hmac_new(key, msg=msg.encode(), digestmod=sha256).hexdigest()
    return [nonce, signature]


async def create_wallet(password: str, callback_link: str) -> Response:
    url = 'https://api.bitaps.com/btc/testnet/v1/create/wallet'
    data = json.dumps({'password': password, 'callback_link': callback_link})

    async with ClientSession() as client:
        response = await client.post(url, data=data)
        return await response.json()


async def create_payment_address(forwarding_address: str) -> Response:
    url = 'https://api.bitaps.com/btc/v1/create/payment/address'
    data = json.dumps({'forwarding_address': forwarding_address})

    async with ClientSession() as client:
        response = await client.post(url, data=data)
        return await response.json()


async def state_wallet(wallet_id: str, nonce: str, signature: HMAC) -> Response:
    url = f'https://api.bitaps.com/btc/testnet/v1/wallet/state/{wallet_id}'
    headers = {'Access-Nonce': nonce, 'Access-Signature': signature}

    async with ClientSession() as client:
        response = await client.get(url, headers=headers)
        return await response.json()


async def send_btc(wallet_id: str, to: str, nonce: str, signature: HMAC) -> Response:
    url = f'https://api.bitaps.com/btc/testnet/v1/wallet/send/payment/{wallet_id}'
    data = json.dumps({'wallet_id': wallet_id, 'receivers_list': [{'address': to, 'amount': 750000}]})
    headers = {'Access-Nonce': nonce, 'Access-Signature': signature}

    async with ClientSession() as client:
        response = await client.post(url, data=data, headers=headers)
        return await response.json()
