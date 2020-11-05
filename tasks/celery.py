import logging

import asyncio

from celery import Celery
from celery.schedules import crontab, timedelta

from tasks.utils.mailling import post_news_teller, test_
from tasks.utils.parsing import parse_news
from tasks.utils.post import delete_not_paid_posts

from data import config


logging.basicConfig(level=logging.INFO, filename='tasks.log')
app = Celery('tasks', broker=config.redis['host'], )

app.conf.timezone = config.TIMEZONE
app.conf.beat_schedule = {
    'test': {
        'task': 'tasks.test',
        'schedule': timedelta(seconds=10)
    },
    'parse_news': {
        'task': 'tasks.parse_news_task',
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


@app.task
def test() -> None:
    loop = asyncio.get_event_loop()
    loop.run_until_complete(test_())
    loop.close()


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
