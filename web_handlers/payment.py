import asyncio

import json

from datetime import datetime

from aiohttp import ClientSession

from hashlib import sha256
import hmac


async def create_wallet(password=None):
    url = 'https://api.bitaps.com/btc/testnet/v1/create/wallet'

    if password:
        data = json.dumps(
            {
                'password': password,
                'callback_link': 'http://62.113.112.244:8002/'
            }
        )
    else:
        data = json.dumps(
            {
                'callback_link': 'http://62.113.112.244:8002/'
            }
        )

    async with ClientSession() as client:
        response = await client.post(url, data=data)
        return await response.json()


async def create_payment_address(wallet_id):
    url = 'https://api.bitaps.com/btc/testnet/v1/create/wallet/payment/address'
    data = json.dumps(
        {
            'wallet_id': wallet_id
        }
    )

    async with ClientSession() as client:
        response = await client.post(url, data=data)
        return await response.json()


async def state_wallet(wallet_id, nonce=None, HMAC_signature=None):
    url = f'https://api.bitaps.com/btc/testnet/v1/wallet/state/{wallet_id}'
    # headers = json.dumps({
    #     'Access-Nonce': nonce,
    #     'Access-Signature': HMAC_signature
    # })

    async with ClientSession() as client:
        response = await client.get(url)
        return await response.json()


async def send_btc(wallet_id, to, nonce=None, HMAC_signature=None):
    url = f'https://api.bitaps.com/btc/testnet/v1/wallet/send/payment/{wallet_id}'
    # headers = json.dumps({
    #     'Access-Nonce': nonce,
    #     'Access-Signature': HMAC_signature
    # })
    data = json.dumps(
        {
            'wallet_id': wallet_id,
            'receivers_list': [
                {
                    'address': to,
                    'amount': 750000
                }
            ],
            'message': {'format': "text", "payload": 'hello'}
        }
    )
    async with ClientSession() as client:
        response = await client.post(url, data=data)
        return await response.json()


if __name__ == '__main__':
    if wallet_nonce >= access_nonce:
        raise APIException(AUTHORIZATION_FAILED,
                           'authorization failed, nonce to low [last used nonce %s]' % wallet_nonce, status=403)
    msg = "%s%s%s" % (redeem_code, msg, access_nonce)
    sign = hmac.new(wallet["password_hash"], msg=msg.encode(), digestmod=hashlib.sha256).digest()
    if sign != access_signature:
        # check old format
        msg = "%s%s" % (redeem_code, access_nonce)
        sign = hmac.new(wallet["password_hash"], msg=msg.encode(), digestmod=hashlib.sha256).digest()
        if sign != access_signature:
            raise APIException(AUTHORIZATION_FAILED, 'authorization failed (HMAC signature invalid)',
                               status=403)
    PASSWORD = None

    data = asyncio.run(create_wallet(PASSWORD))

    WALLET_ID_new = 'BTCvwNrh4MyrUPQX7TzSrLpoMoB3e6M8rsc2W5PQs44js19Ktq6AE'
    # print(WALLET_ID_new)
    WALLET_ID = 'BTCuigJjttZueYhupkZyibsioDpgBVSSFK1vupNohum63h5BEgeyA'

    # key = sha256(
    #     sha256(
    #         (WALLET_ID + PASSWORD).encode()
    #     ).digest()
    # )
    #
    # nonce = datetime.now().time().microsecond
    # msg = WALLET_ID + str(nonce)
    #
    # HMAC_signature = hmac_new(key.digest(), msg.encode())

    # response = asyncio.run(state_wallet(WALLET_ID, str(nonce), HMAC_signature.hexdigest()))
    # print(WALLET_ID)
    # print(data)
    # response = asyncio.run(create_payment_address(WALLET_ID_new))
    # print(response)
    to_new = '2NCb5zhqDNzrRBAUPVyGqpb3u2tBRZ25qF1'
    to = '2MzvSWHjwWyphYB2r55z1pqkXJ9s7htTSa6'
    # print(to)
    # response = asyncio.run(send_btc(WALLET_ID_new, to))
    # print(response)
    response = asyncio.run(state_wallet(WALLET_ID))
    print(response)
    response = asyncio.run(state_wallet(WALLET_ID_new))
    print(response)
