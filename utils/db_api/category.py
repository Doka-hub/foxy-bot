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


async def subscribe_user_to_category(user_id: int, category_key: str) -> None:
    user, created = await get_or_create_user(user_id)
    user_language = user.language
    category = await objects.get(Category, key=category_key, language=user_language)

    if category not in user.subscribed:
        user.subscribed.add([category])
    else:
        user.subscribed.remove([category])


async def set_user_time_to_mail(user_id: int, time_to_mail: str) -> None:
    user, created = await get_or_create_user(user_id)

    user.time_to_mail = time_to_mail
    await objects.update(
        user, ['time_to_mail']
    )

