import logging

import asyncio

from datetime import datetime

from celery import Celery
from celery.schedules import crontab

from models import objects, Post

from utils.post.time_to_pay import timedelta_to_hours

from tasks.utils.mailling import post_news_teller
from tasks.utils.parsing import parse_news

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
        'task': 'tasks.delete_not_paid_posts_task',
        'schedule': crontab(hour='23', minute='59')
    },
    'mailing_morning': {
        'task': 'tasks.mailing_task',
        'schedule': crontab(hour='8', minute='12'),
        'args': ('morning',)
    },
    'mailing_evening': {
        'task': 'tasks.mailing_task',
        'schedule': crontab(hour='20', minute='12'),
        'args': ('evening',)
    },
}


async def delete_not_paid_posts():
    posts = await objects.execute(Post.select().where(not Post.paid))
    for post in posts:
        if timedelta_to_hours(datetime.now() - post.created) >= 72:
            await objects.delete(post)


@app.task
def parse_news_task() -> None:
    loop = asyncio.get_event_loop()
    loop.run_until_complete(parse_news())
    loop.close()


@app.task
def mailing_task(time_to_mail: str) -> None:
    loop = asyncio.get_event_loop()
    loop.run_until_complete(post_news_teller(time_to_mail))
    loop.close()


@app.task
def delete_not_paid_posts_task() -> None:
    loop = asyncio.get_event_loop()
    loop.run_until_complete(delete_not_paid_posts())
    loop.close()
