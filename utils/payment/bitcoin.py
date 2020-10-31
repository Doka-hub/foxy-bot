import asyncio

import json

import time

from aiohttp import ClientSession
from aiohttp.web_response import Response

from hashlib import sha256
from hmac import new as hmac_new


async def create_wallet(password: str = None) -> Response:
    url = 'https://api.bitaps.com/btc/testnet/v1/create/wallet'

    if password:
        data = json.dumps(
            {
                'password': password,
                'callback_link': 'https://getsub.cc/payment/handler/'
            }
        )
    else:
        data = json.dumps(
            {
                'callback_link': 'https://getsub.cc/payment/handler/'
            }
        )

    async with ClientSession() as client:
        response = await client.post(url, data=data)
        return await response.json()


async def create_payment_address(wallet_id: str) -> Response:
    url = 'https://api.bitaps.com/btc/testnet/v1/create/wallet/payment/address'
    data = json.dumps(
        {
            'wallet_id': wallet_id
        }
    )

    async with ClientSession() as client:
        response = await client.post(url, data=data)
        return await response.json()


async def state_wallet(wallet_id: str, headers: dict) -> Response:
    url = f'https://api.bitaps.com/btc/testnet/v1/wallet/state/{wallet_id}'
    async with ClientSession() as client:
        response = await client.get(url, headers=headers)
        return await response.json()


async def send_btc(wallet_id: str, to: str, amount: int, headers: dict = None) -> Response:
    url = f'https://api.bitaps.com/btc/testnet/v1/wallet/send/payment/{wallet_id}/'
    data = json.dumps(
        {
            'wallet_id': wallet_id,
            'receivers_list': [
                {
                    'address': to,
                    'amount': amount
                }
            ]
        }
    )
    async with ClientSession() as client:
        response = await client.post(url, data=data)
        return await response.json()


if __name__ == '__main__':
    async def main(password: str = "123foxy123") -> None:
        wallet_data = await create_wallet(password)
        wallet_id = wallet_data['wallet_id']
        wallet_id_hash = wallet_data['wallet_id_hash']

        nonce = int(time.time() * 1000)
        key = sha256(sha256((wallet_id + password).encode()).digest()).digest()
        msg = wallet_id_hash + str(nonce)

        signature = hmac_new(key, msg=msg.encode(), digestmod=sha256).hexdigest()

        headers = {"Access-Nonce": str(nonce), "Access-Signature": signature}
        status = await state_wallet(wallet_id_hash, headers)
        print(status)


    asyncio.run(main())
    #
    #
    # PASSWORD = None
    #
    # data = asyncio.run(create_wallet(PASSWORD))
    #
    # WALLET_ID_new = 'BTCvwNrh4MyrUPQX7TzSrLpoMoB3e6M8rsc2W5PQs44js19Ktq6AE'
    # # print(WALLET_ID_new)
    # WALLET_ID = 'BTCuigJjttZueYhupkZyibsioDpgBVSSFK1vupNohum63h5BEgeyA'
    #
    # # key = sha256(
    # #     sha256(
    # #         (WALLET_ID + PASSWORD).encode()
    # #     ).digest()
    # # )
    # #
    # # nonce = datetime.now().time().microsecond
    # # msg = WALLET_ID + str(nonce)
    # #
    # # HMAC_signature = hmac_new(key.digest(), msg.encode())
    #
    # # response = asyncio.run(state_wallet(WALLET_ID, str(nonce), HMAC_signature.hexdigest()))
    # # print(WALLET_ID)
    # # print(data)
    # # response = asyncio.run(create_payment_address(WALLET_ID_new))
    # # print(response)
    # to_new = '2NCb5zhqDNzrRBAUPVyGqpb3u2tBRZ25qF1'
    # to = '2MzvSWHjwWyphYB2r55z1pqkXJ9s7htTSa6'
    # # print(to)
    # # response = asyncio.run(send_btc(WALLET_ID_new, to))
    # # print(response)
    # response = asyncio.run(state_wallet(WALLET_ID))
    # print(response)
    # response = asyncio.run(state_wallet(WALLET_ID_new))
    # print(response)
