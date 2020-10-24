from models import objects, Channel, Category

from .users import get_or_create_user


async def check_user_subscribe(user_id: int) -> bool:
    user, created = await get_or_create_user(user_id)

    if user.language == 'ru':
        return user.ru_subscribed
    elif user.language == 'en':
        return user.en_subscribed
    elif user.language == 'he':
        return user.he_subscribed


async def get_channel_to_subscribe(language: str) -> Channel:
    channel = await objects.get(
        Channel, language=language
    )
    return channel
