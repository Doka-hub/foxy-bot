import logging

import asyncio

from datetime import datetime

from celery import Celery
from celery.schedules import crontab

from urllib3.util import parse_url

from models import objects, News, Article, LastPost, Post

from utils.parsing import Parsing, create_article_and_get_article_url
from utils.post.time_to_pay import timedelta_to_hours

from .mailling import post_news_teller, post_to_channel

from data import config


logging.basicConfig(level=logging.INFO, filename='tasks.log')
app = Celery('tasks', broker=config.redis['host'])

app.conf.timezone = config.TIMEZONE
app.conf.beat_schedule = {
    'parse_news': {
        'task': 'tasks.parse_news',
        'schedule': crontab(minute='50')
    },
    'delete_not_paid_posts': {
        'task': 'tasks.delete_not_paid_posts',
        'schedule': crontab(hour='23', minute='59')
    },
    'mailing_morning': {
        'task': 'tasks.mailing',
        'schedule': crontab(hour='8', minute='12'),
        'args': ('morning',)
    },
    'mailing_evening': {
        'task': 'tasks.mailing',
        'schedule': crontab(hour='20', minute='12'),
        'args': ('evening',)
    },
}


# @app.task
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


# @app.task
async def delete_not_paid_posts():
    posts = await objects.execute(Post.select().where(not Post.paid))
    for post in posts:
        if timedelta_to_hours(datetime.now() - post.created) >= 72:
            await objects.delete(post)


@app.task
def mailing(time_to_mail: str) -> None:
    loop = asyncio.get_event_loop()
    loop.run_until_complete(post_news_teller(time_to_mail))
    loop.close()
