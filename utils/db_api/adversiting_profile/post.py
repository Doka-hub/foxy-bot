from typing import Dict

from datetime import datetime

from utils.db_api.user.user import get_or_create_user
from utils.payment.bitcoin import create_payment_address, get_ad_cost

from models import objects, PaymentAddress, Post

from data import config


async def set_phone_number(user_id: int, phone_number: str) -> None:
    user, created = await get_or_create_user(user_id)
    user.phone_number = phone_number
    await objects.update(user, ['phone_number'])


async def save_post_data(user_id: int, post_data: Dict) -> Post:
    """
    :param user_id:
    :param post_data:
    :return: создаёт пост и возвращает адресс для оплаты поста
    """
    user, created = await get_or_create_user(user_id)

    # создаём адресс для оплаты
    payment_address = await create_payment_address(config.BTC_WALLET_ID, config.BTC_CALLBACK_LINK)
    payment_address_data = {
        'wallet_id': config.BTC_WALLET_ID,
        'wallet_id_hash': config.BTC_WALLET_ID_HASH,

        'invoice': payment_address['invoice'],
        'payment_code': payment_address['payment_code'],
        'confirmations': payment_address['confirmations'],

        'address': payment_address['address'],
        'forwarding_address': config.BTC_WALLET_ID,
        'amount': await get_ad_cost(),

        'created': datetime.now(),
        'updated': datetime.now()
    }
    payment_address = await objects.create(PaymentAddress, **payment_address_data)

    channel_id = post_data.get('channel_id')
    title = post_data.get('title', '')
    text = post_data.get('text', '')
    button = post_data.get('button', '')
    date = datetime.strptime(post_data.get('date'), '%d.%m.%Y')
    time = post_data.get('time', 'morning')
    image_id = post_data.get('image_id', None)
    bgcolor = 'gray' if user_id in config.ADMINS.values() else 'yellow'

    post_data = {
        'user': user,
        'channel': channel_id,
        'payment_address': payment_address,
        'title': title,
        'text': text,
        'button': button,
        'image_id': image_id,
        'date': date,
        'time': time,
        'bgcolor': bgcolor,
        'created': datetime.now(),
        'updated': datetime.now(),
    }
    post = await objects.create(Post, **post_data)
    return post


async def update_post_data(post_data: Dict) -> None:
    post_id = post_data.get('post_id')
    post = await objects.get(Post, id=post_id)

    user_id = post.user.user_id

    title = post_data.get('title')
    text = post_data.get('text')
    button = post_data.get('button')
    date = post_data.get('date')
    time = post_data.get('time', 'morning')
    image_id = post_data.get('image_id', '0')
    bgcolor = 'gray' if user_id in config.ADMINS.values() else 'yellow'

    post_data = {
        'title': title,
        'text': text,
        'button': button,
        'image_id': image_id,
        'date': date,
        'time': time,
        'bgcolor': bgcolor,
        'updated': datetime.now(),
        'status': 'processing',
        'status_message': ''
    }
    post = post.pre_update_data(post_data)
    await objects.update(post, list(post_data.keys()))
