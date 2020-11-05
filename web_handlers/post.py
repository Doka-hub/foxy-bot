from aiohttp import web

import aiohttp_jinja2
import jinja2

from models import objects, Post, TGUser

from loader import bot

from data import config


post_app = web.Application()
aiohttp_jinja2.setup(post_app, loader=jinja2.FileSystemLoader('templates'))


@aiohttp_jinja2.template('post/post-list.html')
async def get_post_list(request: web.Request) -> dict:
    response = {}

    admin_list = list(config.ADMINS.values())
    query = Post.select().where(Post.paid).join(TGUser).orwhere(TGUser.user_id.in_(admin_list)).order_by(-Post.id)
    post_list = await objects.execute(query)

    response['post_list'] = post_list
    return response


@aiohttp_jinja2.template('post/post-detail.html')
async def get_post_detail(request: web.Request) -> dict:
    response = {}
    post_id = request.match_info['post_id']
    post = await objects.get(Post, id=post_id)

    if post.image_id != '0':  # если фото не было добавлено в рекламный пост
        # получаем ссылку на фото, чтобы показать в панели
        image = await bot.get_file(post.image_id)
        image_url = bot.get_file_url(image.file_path)
        response['image_url'] = image_url

    response['post'] = post
    return response


@aiohttp_jinja2.template('post/post-detail.html')
async def post_post_detail(request: web.Request) -> get_post_detail:
    post_data = await request.post()
    post_id = request.match_info['post_id']
    post = await objects.get(Post, id=post_id)

    if post_data.get('accept'):
        post.status = 'accepted'
        post.bgcolor = 'green'
    elif post_data.get('decline'):
        post.status = 'declined'
        post.bgcolor = 'red'

    paid = post_data.get('paid')
    if paid == 'false':
        post.paid = False
    elif paid == 'true':
        post.paid = True

    post.status_message = post_data.get('status_message')
    await objects.update(post, ['status', 'status_message', 'paid', 'bgcolor'])

    return await get_post_detail(request)


post_app.add_routes(
    [
        web.get('/list/', get_post_list),

        web.get('/{post_id}/', get_post_detail),
        web.post('/{post_id}/', post_post_detail),
    ]
)
