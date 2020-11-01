from peewee import DoesNotExist

from models import objects, LastPost


async def is_new_post(post_url: str) -> bool:
    """
    :param post_url:
    :return: возвращает булево значение новый ли пост
    """
    try:
        status = await objects.get(LastPost, post_url=post_url)  # если есть урл, это значит что пост уже был
    except DoesNotExist:
        status = False
    return status
