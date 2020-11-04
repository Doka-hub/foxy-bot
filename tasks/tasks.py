import asyncio

from celery import Celery
from celery.schedules import crontab

from urllib3.util import parse_url

from models import objects, News, Article, LastPost

from utils.parsing import Parsing, create_article_and_get_article_url

from .mailling import post_news_teller

from data import config

app = Celery('tasks', broker=config.redis['host'])

app.conf.timezone = config.TIMEZONE
app.conf.beat_schedule = {
    'parse_news': {
        'tasks': 'tasks.parse_news',
        'schedule': crontab(minute='50')
    },
    'mailing_morning': {
        'tasks': 'tasks.mailing',
        'schedule': crontab(hour='8', minute='12'),
        'args': ('morning',)
    },
    'mailing_evening': {
        'tasks': 'tasks.mailing',
        'schedule': crontab(hour='20', minute='12'),
        'args': ('evening',)
    },
}


# @app.tasks
async def parse_news():
    for news in await objects.execute(News.select()):
        parser = Parsing(news.url, news.site)
        posts = await parser.parse()
        if posts:
            for post in posts[::-1]:  # берём старые посты в первую очередь
                # page_url = create_article_and_get_article_url(post[0], post[1])  # title, content
                page_url = post[-1]
                if news.site in ['https://www.ynet.co.il']:  # для этого сайта нужно перекодировать урл
                    page_url = parse_url(page_url).url

                await objects.get_or_create(Article, url=page_url, category=news.category)

            last_post = await objects.get(LastPost, news=news)
            last_post.post_url = post[-1]  # post_url
            await objects.update(last_post, ['post_url'])


# asyncio.run(parse_news())


# @app.tasks
def mailing(time_to_mail):
    # loop = asyncio.get_event_loop()
    # loop.run_until_complete(parse_news())
    # loop.close()
    asyncio.create_task(parse_news())
