from models import objects, Category

from .user import get_or_create_user


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
    await objects.update(user, ['time_to_mail'])
