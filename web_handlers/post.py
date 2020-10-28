from aiohttp import web
import aiohttp_jinja2
import jinja2

from datetime import datetime
from uuid import uuid4

from models import objects, Post, User
from loader import bot
from data import config
from utils.db_api.users import get_or_create_user

post_app = web.Application()
aiohttp_jinja2.setup(post_app, loader=jinja2.FileSystemLoader('templates'))


@aiohttp_jinja2.template('post-list.html')
async def get_post_list(request: web.Request):
    response = {}

    admin_list = list(config.ADMINS.values())
    query = Post.select().where(Post.paid).join(User).orwhere(User.user_id.in_(admin_list)).order_by(-Post.id)
    post_list = await objects.execute(query)

    response['post_list'] = post_list
    return response


@aiohttp_jinja2.template('post-create.html')
async def get_post_create(request: web.Request):
    response = {'TIME_CHOICES': Post.TIME_CHOICES, 'STATUS_CHOICES': Post.STATUS_CHOICES}
    return response


@aiohttp_jinja2.template('post-create.html')
async def post_post_create(request: web.Request):
    response = {'TIME_CHOICES': Post.TIME_CHOICES, 'STATUS_CHOICES': Post.STATUS_CHOICES}
    post_data = await request.post()

    user, created = await get_or_create_user(config.ADMINS.get('foxy'))

    uuid_pay = str(uuid4())

    date = datetime.strptime(post_data.get('date'), '%Y-%m-%d')

    button_text = post_data['button_text']
    button_url = post_data['button_url']
    button = f'{button_text} - {button_url}'

    data = {
        'user': user,
        'uuid_pay': uuid_pay,
        'title': post_data.get('title'),
        'text': post_data.get('text'),
        'button': button,
        'image_id': 0,
        'date': date,
        'time': post_data.get('time', 'morning'),

        'status': post_data.get('status'),
        'status_message': post_data.get('status_message'),
        'paid': post_data.get('paid')
    }

    await objects.create(Post, **data)
    return response


@aiohttp_jinja2.template('post-detail.html')
async def get_post_detail(request: web.Request):
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


@aiohttp_jinja2.template('post-detail.html')
async def post_post_detail(request: web.Request):
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

        web.get('/create/', get_post_create),
        web.post('/create/', post_post_create),

        web.get('/{post_id}/', get_post_detail),
        web.post('/{post_id}/', post_post_detail),
    ]
)
