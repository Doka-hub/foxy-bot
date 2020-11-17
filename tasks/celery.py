import logging

import asyncio

from celery import Celery
from celery.schedules import crontab, timedelta

from .utils.mailling import send_post_news_teller
from .utils.parsing import parse_news
from .utils.post import delete_not_paid_posts

from data import config


logging.basicConfig(level=logging.INFO, filename='tasks.log')


app = Celery('celery', broker=config.redis['host'], )

app.conf.timezone = config.TIMEZONE
app.conf.beat_schedule = {
    # 'test': {
    #     'task': 'test',
    #     'schedule': timedelta(seconds=10.0)
    # },
    'parse_news': {
        'task': 'parse_news',
        'schedule': crontab(minute='34')
    },
    'delete_not_paid_posts': {
        'task': 'delete_not_paid_posts_task',
        'schedule': crontab(hour='23', minute='59')
    },
    'mailing_morning': {
        'task': 'mailing',
        'schedule': crontab(hour='8', minute='10'),
        'args': ('morning',)
    },
    'mailing_evening': {
        'task': 'mailing',
        'schedule': crontab(hour='20', minute='10'),
        'args': ('evening',)
    },
}


# @app.task(name='test')
# def test() -> None:
#    print(2)


@app.task(name='parse_news')
def parse_news_task() -> None:
    loop = asyncio.get_event_loop()
    loop.run_until_complete(parse_news())
    print('end: parse')


@app.task(name='mailing')
def mailing_task(time_to_mail: str) -> None:
    loop = asyncio.get_event_loop()
    loop.run_until_complete(send_post_news_teller(time_to_mail))
    print('end: mailing')


@app.task(name='delete_not_paid_posts')
def delete_not_paid_posts_task() -> None:
    loop = asyncio.get_event_loop()
    loop.run_until_complete(delete_not_paid_posts())
    print('end: mailing')
