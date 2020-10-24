from models import objects

from .users import get_or_create_user


async def subscribe_user_to_channel(user_id: int) -> None:
    user, created = await get_or_create_user(user_id)

    if user.language == 'ru':
        user.ru_subscribed = True
    elif user.language == 'en':
        user.en_subscribed = True
    elif user.language == 'he':
        user.he_subscribed = True

    await objects.update(
        user, [
            'ru_subscribed',
            'en_subscribed',
            'he_subscribed'
        ]
    )
