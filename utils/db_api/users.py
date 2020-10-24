from models import objects, User
from utils.payment import bitcoin

from typing import Optional, List, Union

from data import config


async def get_or_create_user(user_id: int, username: Optional[str] = None) -> List[Union[User, bool]]:
    user, created = await objects.get_or_create(User, user_id=user_id)

    if username and user.username != username:
        user.username = username
        await objects.update(user, ['username'])
    if created:  # если создан сейчас
        btc_address_to_pay = await bitcoin.create_payment_address(config.BTC_WALLET_ID)
        user.btc_address_to_pay = btc_address_to_pay['address']
        await objects.update(user, ['btc_address_to_pay'])
    return [user, created]
