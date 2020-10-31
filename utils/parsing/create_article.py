from telegraph import Telegraph


def create_article_and_get_article_url(title: str, html_content: str) -> str:
    """
    :param title:
    :param html_content:
    :return: возвращает ссылку на статью
    """
    telegraph = Telegraph()
    telegraph.create_account(short_name='test')

    response = telegraph.create_page(title, html_content=html_content)
    return response['url']
