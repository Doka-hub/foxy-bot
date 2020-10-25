from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from typing import List, Union, Dict

from utils.keyboards.inline import get_inline_keyboard
from utils.db_api.users import get_or_create_user
from utils.db_api.language import get_language

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


def get_edit_post_inline_button(user_language: str, post_id: Union[int, str]) -> List[InlineKeyboardButton]:
    edit_text = config.messages[user_language]['post_detail_text']['edit']
    post_edit_inline_button = [
        InlineKeyboardButton(
            edit_text,
            callback_data=f'edit_post {post_id}'
        )
    ]
    return post_edit_inline_button


async def get_list_post_inline_keyboard(user_id: int) -> InlineKeyboardMarkup:
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
        edit_post_inline_button = get_edit_post_inline_button(user_language, post.id)
        inline_buttons.insert(
            0,
            edit_post_inline_button
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

    create_post_preview = config.messages[user_language]['create_post_preview']
    date_publication_text = create_post_preview['date']
    time_publication_text = create_post_preview['time']

    message = \
        f'*{title}*\n\n{text}' if title and text else \
        f'*{title}*\n\n' if title and not text else \
        f'{text}' if text and not title else \
        f'{config.messages[user_language]["advertising_profile"]["create_post"]}:'

    message += f'\n{date_publication_text}: `{date}`' if date else ''
    message += f'\n{time_publication_text}: `{time}`' if time else ''
    return message


def get_post_create_inline_keyboard(user_language: str, post_data: Dict) -> InlineKeyboardMarkup:
    create_post_menu = config.messages[user_language]['create_post']
    edit_post_menu = config.messages[user_language]['edit_post']
    if post_data.get('button'):
        post_detail_inline_button = get_post_detail_inline_button(post_data.get('button'))

    create_post_inline_keyboard = get_inline_keyboard(
        [
            post_detail_inline_button if post_data.get('button') else [],
            [
                InlineKeyboardButton(
                    create_post_menu['image'] if not post_data.get('image_id') else edit_post_menu['image'],
                    callback_data='create_post_image' if not post_data.get('image_id') else 'edit_post_image'
                ),
            ],
            [
                InlineKeyboardButton(
                    create_post_menu['title'] if not post_data.get('title') else edit_post_menu['title'],
                    callback_data='create_post_title' if not post_data.get('title') else 'edit_post_title'
                ),
                InlineKeyboardButton(
                    create_post_menu['text'] if not post_data.get('text') else edit_post_menu['text'],
                    callback_data='create_post_text' if not post_data.get('text') else 'edit_post_text'
                )
            ],
            [
                InlineKeyboardButton(
                    create_post_menu['button'] if not post_data.get('button') else edit_post_menu['button'],
                    callback_data='create_post_button' if not post_data.get('button') else 'edit_post_button'
                )
            ],
            [
                InlineKeyboardButton(
                    create_post_menu['date'] if not post_data.get('date') else edit_post_menu['date'],
                    callback_data='create_post_date' if not post_data.get('date') else 'edit_post_date'
                )
            ],
            [
                InlineKeyboardButton(
                    create_post_menu['moderate'], callback_data='post_moderate'
                )
            ],
            [
                InlineKeyboardButton(
                    config.messages[user_language]['cancel'], callback_data='post_cancel'
                )
            ],
        ]
    )
    return create_post_inline_keyboard
