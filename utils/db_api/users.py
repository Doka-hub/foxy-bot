from models import objects, User
from utils.payment import bitcoin

from data import config


async def get_or_create_user(user_id: int, username: str = None) -> [User, bool]:
    user = await objects.get_or_create(User, user_id=user_id)

    if username and user[0].username != username:
        user[0].username = username
        await objects.update(user[0], ['username'])
    if user[1]:  # если создан сейчас
        btc_address_to_pay = await bitcoin.create_payment_address(config.BTC_WALLET_ID)

        user[0].btc_address_to_pay = btc_address_to_pay['address']
        await objects.update(user[0], ['btc_address_to_pay'])
    return user


async def set_language(user_id: int, language: str):
    user = (await get_or_create_user(user_id))[0]
    user.language = language
    await objects.update(user, ['language'])
