from urllib3.util import parse_url

from utils.parsing import Parsing, create_article_and_get_article_url

from tasks.utils.mailling import post_news_teller, post_to_channel

from models import objects, News, Article, LastPost


async def parse_news():
    for news in await objects.execute(News.select()):
        parser = Parsing(news.url, news.site)
        posts = await parser.parse()
        if posts:
            for post in posts[::-1]:  # берём старые посты в первую очередь
                article_url = create_article_and_get_article_url(post[0], post[1])  # title, content
                if news.site in ['https://www.ynet.co.il']:  # для этого сайта нужно перекодировать урл
                    article_url = parse_url(article_url).url

                await objects.get_or_create(Article, url=article_url, category=news.category)
                await post_to_channel(news.category.language, post[2], article_url)
            last_post = await objects.get(LastPost, news=news)
            last_post.post_url = post[-1]  # post_url
            await objects.update(last_post, ['post_url'])

    await post_news_teller('upon_receipt_of')
