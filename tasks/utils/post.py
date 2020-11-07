from datetime import datetime

from models import objects, Post

from utils.post.time_to_pay import timedelta_to_hours


async def delete_not_paid_posts():
    posts = await objects.execute(Post.select().where(Post.paid == False))
    for post in posts:
        if timedelta_to_hours(datetime.now() - post.created) >= 72:
            await objects.delete(post)
