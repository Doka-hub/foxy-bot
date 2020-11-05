from models import objects, Channel, Article

from utils.db_api.user.channel import get_channel_to_subscribe, check_user_channel_subscribed

from loader import bot


def make_message(language: str, preview_text: str, article_url: str) -> str:
    ru_message = preview_text + '\n\n' + f'[Читать...]({article_url})'
    en_message = preview_text + '\n\n' + f'[Read...]({article_url})'
    he_message = preview_text + '\n\n' + f'[Read...]({article_url})'
    return (
        ru_message if language == 'ru' else
        en_message if language == 'en' else
        he_message
    )


async def post_to_channel(language: str, preview_text: str, article_url: str) -> None:
    channel = await objects.get(Channel, language=language)
    channel_id = channel.channel_id
    await bot.send_message(channel_id, make_message(language, preview_text, article_url))
    await bot.close()


async def post_to_user(user_id: int, language: str, preview_text: str, article_url: str) -> None:
    await bot.send_message(user_id, make_message(language, preview_text, article_url))
    await bot.close()


async def post_news_teller(time_to_mail: str) -> None:
    for article in await objects.execute(Article.select()):
        for user in article.category.users:
            article_language = article.category.language

            channel = await get_channel_to_subscribe(article_language)
            channel_id = channel.channel_id

            if check_user_channel_subscribed(bot, user.user_id, channel_id):
                if user.time_to_mail == time_to_mail:
                    await post_to_user(user.user_id, article.category.language, f'#{article.category.name}',
                                       article.url)

    if time_to_mail == 'morning':  # очищаем статьи после утренней рассылки
        Article.truncate_table()


async def test_():
    print(2)
    await bot.send_message(1092694232, 'hello')
    await bot.close()
