from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from datetime import datetime, timedelta

from typing import List, Union, Dict, Optional

from utils.keyboards.inline import get_inline_keyboard
from utils.db_api.user import get_or_create_user
from utils.post.time_to_pay import timedelta_to_hours

from models import objects, Post, Channel

from data import config


def get_post_detail_inline_button(button: str) -> List[InlineKeyboardButton]:
    button_text, button_url = button.split(' - ')
    post_detail_inline_button = [InlineKeyboardButton(button_text, url=button_url)]
    return post_detail_inline_button


def get_post_update_inline_button(user_language: str, post_id: Union[int, str]) -> List[InlineKeyboardButton]:
    edit_text = config.messages[user_language]['post_detail_text']['edit']
    post_update_inline_button = [InlineKeyboardButton(edit_text, callback_data=f'post_update {post_id}')]
    return post_update_inline_button


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


async def get_post_detail_text_answer(user_language: str, post: Post) -> str:
    post_detail_text = config.messages[user_language]['post_detail_text']
    if not post.paid:
        pay_text = await get_pay_text_answer(user_language, post)
    else:
        pay_text = ''

    status_title = post_detail_text['status']
    reason_title = post_detail_text['reason']
    date_title = post_detail_text['date']
    time_title = post_detail_text['time']

    time = config.messages[user_language]['time_to_mail'][post.time]
    status = post_detail_text[post.status]

    message = (
            pay_text +
            f'\n\n{status_title}: `{status}`' +
            (f'\n{reason_title}: `{post.status_message}`' if post.status == 'declined' else '') +
            f'\n{date_title}: `{post.get_date()}`' +
            f'\n{time_title}: `{time}`' +
            (f'\n\n*{post.title}*' if post.title else '') +
            (f'\n\n{post.text}\n' if post.text else '')
    )
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
        post_update_inline_button = get_post_update_inline_button(user_language, post.id)
        inline_buttons.insert(
            0,
            post_update_inline_button
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


async def get_post_button_inline_keyboard(button: str) -> Optional[InlineKeyboardMarkup]:
    if not button:
        return None
    button_text, button_url = button.split(' - ')

    post_inline_button = get_inline_keyboard([[InlineKeyboardButton(button_text, url=button_url)]])
    return post_inline_button


def get_confirmation_text_answer(user_language: str) -> str:
    confirmation_texts = config.messages[user_language]['confirmation']
    confirmation_text = confirmation_texts['ask']
    return confirmation_text


def get_confirmation_inline_keyboard(user_language: str) -> InlineKeyboardMarkup:
    """
    :param user_language:
    :return: возвращает клавиатуру для подтверждения создания поста
    """
    confirmation_texts = config.messages[user_language]['confirmation']
    confirmation_yes = confirmation_texts['yes']
    confirmation_no = confirmation_texts['no']

    confirmation_inline_keyboard = get_inline_keyboard([[
        InlineKeyboardButton(confirmation_yes, callback_data='confirmation_accept'),
        InlineKeyboardButton(confirmation_no, callback_data='confirmation_decline')
    ]])
    return confirmation_inline_keyboard


async def get_choose_channel_to_mail_inline_keyboard(user_language: str) -> InlineKeyboardMarkup:
    channels = await objects.execute(Channel.select())

    choose_text = config.messages[user_language]['choose']
    channels = [
        [
            InlineKeyboardButton(
                channel.channel_title, url=channel.channel_url
            ),
            InlineKeyboardButton(
                f'{choose_text} - {channel.language}',
                callback_data=f'choose_channel {channel.id}'  # channel.id not channel.channel_id
            )
        ] for channel in channels
    ]

    choose_channel_to_mail_inline_keyboard = get_inline_keyboard(
        channels + [
            [InlineKeyboardButton(config.messages[user_language]['cancel'], callback_data='advertising_profile')]
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
    post_update_menu = config.messages[user_language]['post_update']
    if post_data.get('button'):
        post_detail_inline_button = get_post_detail_inline_button(post_data.get('button'))

    post_create_inline_keyboard = get_inline_keyboard(
        [
            post_detail_inline_button if post_data.get('button') else [],
            [
                InlineKeyboardButton(
                    post_create_menu['image'] if not post_data.get('image_id') else post_update_menu['image'],
                    callback_data='post_create_image' if not post_data.get('image_id') else 'post_update_image'
                ),
            ],
            [
                InlineKeyboardButton(
                    post_create_menu['title'] if not post_data.get('title') else post_update_menu['title'],
                    callback_data='post_create_title' if not post_data.get('title') else 'post_update_title'
                ),
                InlineKeyboardButton(
                    post_create_menu['text'] if not post_data.get('text') else post_update_menu['text'],
                    callback_data='post_create_text' if not post_data.get('text') else 'post_update_text'
                )
            ],
            [
                InlineKeyboardButton(
                    post_create_menu['button'] if not post_data.get('button') else post_update_menu['button'],
                    callback_data='post_create_button' if not post_data.get('button') else 'post_update_button'
                )
            ],
            [
                InlineKeyboardButton(
                    post_create_menu['date'] if not post_data.get('date') else post_update_menu['date'],
                    callback_data='post_create_date' if not post_data.get('date') else 'post_update_date'
                )
            ],
            [
                InlineKeyboardButton(
                    post_create_menu['moderate'],
                    callback_data='post_moderate'
                )
            ],
            [
                InlineKeyboardButton(
                    config.messages[user_language]['cancel'],
                    callback_data='post_cancel'
                )
            ],
        ]
    )
    return post_create_inline_keyboard


async def get_date_inline_keyboard(user_id: int, post_data: Dict) -> InlineKeyboardMarkup:
    user, created = await get_or_create_user(user_id)
    user_language = user.language
    channel_id = post_data.get('channel_id')

    posts = await objects.execute(Post.select().where(Post.paid == True).join(Channel).where(Channel.id == channel_id))
    posts = [(post.get_date(), post.time) for post in posts]

    today = datetime.today().date()
    date_list = []
    for day in range(30):
        for time in ['morning', 'evening']:
            date = today + timedelta(days=day)
            date_list.append(
                (date, time)
            )
    for date in date_list:
        if (date[0].strftime('%d.%m.%Y'), date[1]) in posts:
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
                dates.append(InlineKeyboardButton(f'{config.messages[user_language]["lock"]} - {time}',
                                                  callback_data='date_busy'))
                date_list.remove(date_list[0])
                continue
            date = date.strftime('%d.%m.%Y')
            dates.append(InlineKeyboardButton(f'{date} - {time}', callback_data=f'choose_date {date}-{time_data}'))
            date_list.remove(date_list[0])

        free_dates_list.append(dates)

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


async def get_post_moderate_answer_text(user_language: int, post: Post) -> str:
    title = post.get('title', '')
    text = post.get('text', '')
    date = post.get('date', '')
    time = post.get('time', '')
    time = config.messages[user_language]['time_to_mail'][time]

    post_create_preview = config.messages[user_language]['post_create_preview']
    date_publication_text = post_create_preview['date']
    time_publication_text = post_create_preview['time']

    message = (
        f'*{title}*\n\n'
        f'{text}'
        f'\n{date_publication_text}: `{date}`'
        f'\n{time_publication_text}: `{time}`'
    )
    return message


async def get_pay_text_answer(user_language: str, post: Post) -> str:
    payment_address = post.payment_address.address
    amount = post.payment_address.amount
    today = datetime.now()
    time_to_pay = 72 - timedelta_to_hours((today - post.created))  # получаем часы

    message = config.messages[user_language]['pay_message']
    message = message.format(btc_address_to_pay=payment_address, amount=amount, time_to_pay=time_to_pay)
    return message
