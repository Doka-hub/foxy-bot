from .users import get_or_create_user

from models import objects, User


async def get_language(user_id: int) -> User.language:
    user, created = await get_or_create_user(user_id)
    return user.language


async def set_language(user_id: int, language: str) -> None:
    user = (await get_or_create_user(user_id))[0]
    user.language = language
    await objects.update(user, ['language'])
