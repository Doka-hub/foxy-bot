from typing import Optional

from asyncio import sleep

from telegraph import Telegraph
from telegraph.exceptions import TelegraphException, InvalidHTML


async def create_article_and_get_article_url(
        title: str, html_content: str, tries: int = 1, max_tries: int = 5) -> Optional[str]:
    """
    :param title:
    :param html_content:
    :param tries:
    :param max_tries:
    :return: возвращает ссылку на статью
    """
    if tries > max_tries:
        return None
    try:
        telegraph = Telegraph()
        telegraph.create_account('Israel News')

        response = telegraph.create_page(title, html_content=html_content)
        return response['url']
    except TelegraphException:
        await sleep(5.0)
        return await create_article_and_get_article_url(title, html_content, tries + 1, max_tries)
    except InvalidHTML:
        return None
