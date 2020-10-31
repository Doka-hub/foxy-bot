import asyncio

from celery import Celery
from celery.schedules import crontab

from urllib3.util import parse_url

from models import objects, News, Article, LastPost

from utils.parsing import Parsing, create_article_and_get_article_url

from .mailling import post_news_teller

from data import config

app = Celery('task', broker=config.redis['host'])

app.conf.timezone = config.TIMEZONE
app.conf.beat_schedule = {
    'parse_news': {
        'task': 'task.parse_news',
        'schedule': crontab(minute='50')
    },
    'mailing_morning': {
        'task': 'task.mailing',
        'schedule': crontab(hour='8', minute='12'),
        'args': ('morning',)
    },
    'mailing_evening': {
        'task': 'task.mailing',
        'schedule': crontab(hour='20', minute='12'),
        'args': ('evening',)
    },
}


# @app.task
async def parse_news():
    for news in await objects.execute(News.select()):
        parser = Parsing(news.url, news.site)
        posts = parser.parse()
        if posts:
            for post in posts[::-1]:
                page_url = create_article_and_get_article_url(post[0], post[1])  # title, content
                if news.site in ['https://www.ynet.co.il']:
                    page_url = parse_url(page_url)
                await objects.get_or_create(Article, url=page_url, category=news.category)

            last_post = await objects.get(LastPost, news=news)
            last_post.article_url = page_url
            await objects.update(last_post, ['page_url'])


asyncio.run(parse_news())


@app.task
def mailing(time_to_mail):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(post_news_teller(time_to_mail))
    loop.close()
