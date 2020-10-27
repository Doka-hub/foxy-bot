from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from datetime import datetime, timedelta

from typing import List, Union, Dict

from utils.keyboards.inline import get_inline_keyboard
from utils.db_api.users import get_or_create_user

from models import objects, Post, Channel

from data import config


def get_post_detail_inline_button(button: str) -> List[InlineKeyboardButton]:
    button_text, button_url = button.split(' - ')
    post_detail_inline_button = [
        InlineKeyboardButton(
            button_text, url=button_url
        )
    ]
    return post_detail_inline_button


def get_post_edit_inline_button(user_language: str, post_id: Union[int, str]) -> List[InlineKeyboardButton]:
    edit_text = config.messages[user_language]['post_detail_text']['edit']
    post_edit_inline_button = [
        InlineKeyboardButton(
            edit_text,
            callback_data=f'edit_post {post_id}'
        )
    ]
    return post_edit_inline_button


async def get_post_list_inline_keyboard(user_id: int) -> InlineKeyboardMarkup:
    user, created = await get_or_create_user(user_id)
    user_language = user.language

    posts = await objects.execute(Post.select().where(Post.user == user))
    posts_inline = [
        [
            InlineKeyboardButton(
                f'# {number + 1} ' + (
                    '✅' if post.status == 'accepted' else
                    '❌' if post.status in ['declined', 'not_paid'] else
                    '⏳'  # processing
                ),
                callback_data=f'post_detail {post.id}'
            )
        ] for number, post in enumerate(posts)
    ]

    list_post_inline_keyboard = get_inline_keyboard(
        posts_inline + [
            [
                InlineKeyboardButton(
                    config.messages[user_language]['menu']['back'],
                    callback_data='advertising_profile'
                )
            ]
        ]
    )
    return list_post_inline_keyboard


def get_post_detail_text_answer(user_language: str, post: Post) -> str:
    post_detail_text = config.messages[user_language]['post_detail_text']
    status_title = post_detail_text['status']
    reason_title = post_detail_text['reason']
    date_title = post_detail_text['date']
    time_title = post_detail_text['time']

    time = config.messages[user_language]['time_to_mail'][post.time]
    status = post_detail_text[post.status]

    message = \
        f'{status_title}: `{status}`\n' + \
        (f'{reason_title}: `{post.status_message}`\n' if post.status == 'declined' else '') + \
        f'{date_title}: `{post.date}`\n' + \
        f'{time_title}: `{time}`\n' + \
        (f'\n*{post.title}*\n' if post.title else '') + \
        (f'\n{post.text}\n' if post.text else '')
    return message


def get_post_inline_buttons(user_language: str, post: Post) -> InlineKeyboardMarkup:
    inline_buttons = [
        [
            InlineKeyboardButton(
                config.messages[user_language]['menu']['back'],
                callback_data='post_list'
            )
        ]
    ]
    # если модерация отказала, то даётся возможность изменить пост
    if post.status == 'declined':
        post_edit_inline_button = get_post_edit_inline_button(user_language, post.id)
        inline_buttons.insert(
            0,
            post_edit_inline_button
        )
    # если есть кнопка, то добавляем её
    if post.button:
        post_detail_inline_button = get_post_detail_inline_button(post.button)
        inline_buttons.insert(
            0,
            post_detail_inline_button
        )
    # собираем все кнопки
    detail_post_inline_keyboard = get_inline_keyboard(inline_buttons)
    return detail_post_inline_keyboard


async def get_choose_channel_to_mail_inline_keyboard(user_language: str) -> InlineKeyboardMarkup:
    channels = await objects.execute(Channel.select())

    choose_text = config.messages[user_language]['choose']
    channels = [
        [
            InlineKeyboardButton(
                f'{channel.channel_title} - {channel.language}', url=channel.channel_url
            ),
            InlineKeyboardButton(
                choose_text, callback_data=f'choose_channel {channel.id}'  # не channel.channel_id (id в таблице)
            )
        ] for channel in channels
    ]

    choose_channel_to_mail_inline_keyboard = get_inline_keyboard(
        channels + [
            [
                InlineKeyboardButton(
                    config.messages[user_language]['cancel'], callback_data='advertising_profile'
                )
            ]
        ]
    )
    return choose_channel_to_mail_inline_keyboard


def get_post_create_message(user_language: str, post_data: Dict) -> str:
    title = post_data.get('title')
    text = post_data.get('text')
    date = post_data.get('date')
    time = post_data.get('time')
    if time:
        time = config.messages[user_language]['time_to_mail'][time]

    post_create_preview = config.messages[user_language]['post_create_preview']
    date_publication_text = post_create_preview['date']
    time_publication_text = post_create_preview['time']

    message = \
        f'*{title}*\n\n{text}' if title and text else \
        f'*{title}*\n\n' if title and not text else \
        f'{text}' if text and not title else \
        f'{config.messages[user_language]["advertising_profile"]["post_create"]}:'

    message += f'\n{date_publication_text}: `{date}`' if date else ''
    message += f'\n{time_publication_text}: `{time}`' if time else ''
    return message


def get_post_create_inline_keyboard(user_language: str, post_data: Dict) -> InlineKeyboardMarkup:
    post_create_menu = config.messages[user_language]['post_create']
    post_edit_menu = config.messages[user_language]['edit_post']
    if post_data.get('button'):
        post_detail_inline_button = get_post_detail_inline_button(post_data.get('button'))

    post_create_inline_keyboard = get_inline_keyboard(
        [
            post_detail_inline_button if post_data.get('button') else [],
            [
                InlineKeyboardButton(
                    post_create_menu['image'] if not post_data.get('image_id') else post_edit_menu['image'],
                    callback_data='post_create_image' if not post_data.get('image_id') else 'post_edit_image'
                ),
            ],
            [
                InlineKeyboardButton(
                    post_create_menu['title'] if not post_data.get('title') else post_edit_menu['title'],
                    callback_data='post_create_title' if not post_data.get('title') else 'post_edit_title'
                ),
                InlineKeyboardButton(
                    post_create_menu['text'] if not post_data.get('text') else post_edit_menu['text'],
                    callback_data='post_create_text' if not post_data.get('text') else 'post_edit_text'
                )
            ],
            [
                InlineKeyboardButton(
                    post_create_menu['button'] if not post_data.get('button') else post_edit_menu['button'],
                    callback_data='post_create_button' if not post_data.get('button') else 'post_edit_button'
                )
            ],
            [
                InlineKeyboardButton(
                    post_create_menu['date'] if not post_data.get('date') else post_edit_menu['date'],
                    callback_data='post_create_date' if not post_data.get('date') else 'post_edit_date'
                )
            ],
            [
                InlineKeyboardButton(
                    post_create_menu['moderate'], callback_data='post_moderate'
                )
            ],
            [
                InlineKeyboardButton(
                    config.messages[user_language]['cancel'], callback_data='post_cancel'
                )
            ],
        ]
    )
    return post_create_inline_keyboard


async def get_date_inline_keyboard(user_language: str, post_data: Dict) -> InlineKeyboardMarkup:
    channel_id = post_data.get('channel_id')

    posts = await objects.execute(Post.select().where(Post.paid).join(Channel).where(Channel.id == channel_id))
    posts = [(post.date, post.time) for post in posts]

    today = datetime.today()
    date_list = []
    for day in range(30):
        for time in ['morning', 'evening']:
            date = (today + timedelta(days=day))
            date_list.append(
                (date, time)
            )
    for date in date_list:
        if (date[0].date(), date[1]) in posts:
            date_list[date_list.index(date)] = ('lock', date[1])
            continue

    free_dates_list = []
    for i in range(30):
        dates = []
        for x in range(2):
            time = config.messages[user_language]['time_to_mail'][date_list[0][1]]
            time_data = date_list[0][1]
            date = date_list[0][0]

            if date_list[0][0] == 'lock':
                dates.append(
                    InlineKeyboardButton(
                        f'{config.messages[user_language]["lock"]} - {time}',
                        callback_data='date_busy'
                    )
                )
                date_list.remove(date_list[0])
                continue
            date = date.strftime('%d.%m.%Y')
            dates.append(
                InlineKeyboardButton(
                    f'{date} - {time}',
                    callback_data=f'choose_date {date}-{time_data}'
                )
            )
            date_list.remove(date_list[0])

        free_dates_list.append(
            dates
        )

    date_inline_keyboard = get_inline_keyboard(
        free_dates_list +
        [
            [
                InlineKeyboardButton(config.messages[user_language]['cancel'], callback_data='data_cancel')
            ]
        ]
    )
    return date_inline_keyboard


def get_post_create_data_cancel_inline_keyboard(user_language: str) -> InlineKeyboardMarkup:
    """
    :param user_language: ['ru', 'en, 'he']
    :return: Возвращает inline-клавиатуру с отменой заполнения того или иного поля
    """
    post_create_data_cancel_inline_keyboard = get_inline_keyboard(
        [
            [
                InlineKeyboardButton(config.messages[user_language]['cancel'], callback_data='data_cancel')
            ]
        ]
    )
    return post_create_data_cancel_inline_keyboard
