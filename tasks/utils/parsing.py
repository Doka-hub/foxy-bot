from asyncio import sleep

import logging

from telegraph.exceptions import TelegraphException, InvalidHTML

from urllib3.util import parse_url

from utils.parsing import Parsing, create_article_and_get_article_url

from tasks.utils.mailling import send_post_to_channel, send_post_news_teller_upon_receipt_of

from models import objects, News, Article, LastPost


logging.basicConfig(level=logging.info, filename='telegraph.log')


async def parse_news():
    posts_upon_receipt_of = []
    for news in await objects.execute(News.select()):
        parser = Parsing(news.url, news.site)
        posts = await parser.parse()
        if posts:
            for post in posts[::-1]:  # берём старые посты в первую очередь
                try:
                    article_url = create_article_and_get_article_url(post[0], post[1])  # title, content
                except TelegraphException as e:
                    logging.info(f'error - {e}')
                    await sleep(5.0)
                    try:
                        article_url = create_article_and_get_article_url(post[0], post[1])  # title, content
                    except TelegraphException as e:
                        logging.info(f'error - {e}')
                        continue
                except InvalidHTML as e:
                    logging.info(f'error - {e}: {news.url} - {post[1]}')
                    continue

                if news.site in ['https://www.ynet.co.il']:  # для этого сайта нужно перекодировать урл
                    article_url = parse_url(article_url).url

                article, created = await objects.get_or_create(Article, url=article_url, category=news.category)
                if created:
                    posts_upon_receipt_of.append(article)
                await send_post_to_channel(news.category.language, post[2], article_url,
                                           news.category.name)  # post[2] - preview_text

            last_post = await objects.get(LastPost, news=news)
            last_post.post_url = post[-1]  # post_url
            await objects.update(last_post, ['post_url'])

    await send_post_news_teller_upon_receipt_of(posts_upon_receipt_of)
