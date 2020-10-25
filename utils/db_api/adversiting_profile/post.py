from utils.db_api.users import get_or_create_user

from models import objects


async def set_phone_number(user_id: int, phone_number: str) -> None:
    user, created = await get_or_create_user(user_id)
    user.phone_number = phone_number
    await objects.update(user, ['phone_number'])
