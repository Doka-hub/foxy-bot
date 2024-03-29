from typing import Dict, Optional

import peewee
from peewee_async import Manager, PostgresqlDatabase, MySQLDatabase

from data import config


database = PostgresqlDatabase(database=config.postgresql_info['db'], user=config.postgresql_info['user'], )
# database = MySQLDatabase(database=config.mysql['db'], user=config.mysql['user'], password=config.mysql['password'])
objects = Manager(database)


class BaseModel(peewee.Model):
    class Meta:
        database = database


class PaymentAmount(BaseModel):
    amount = peewee.DecimalField(default=300)


class PaymentAddress(BaseModel):
    wallet_id = peewee.CharField(max_length=255)
    wallet_id_hash = peewee.CharField(max_length=255)

    invoice = peewee.CharField(max_length=255)
    payment_code = peewee.CharField(max_length=255)
    confirmations = peewee.IntegerField(default=1)

    address = peewee.CharField(max_length=255)
    forwarding_address = peewee.CharField(max_length=255)

    amount = peewee.DecimalField()
    amount_got = peewee.DecimalField(default=0)

    created = peewee.DateTimeField()
    updated = peewee.DateTimeField()


class Category(BaseModel):
    key = peewee.CharField(max_length=255, null=True)
    name = peewee.CharField(max_length=255, null=True)
    language = peewee.CharField(max_length=2)
    is_active = peewee.BooleanField(default=True)


class News(BaseModel):
    # При парсинге учитывается сайт. В зависимости от сайта выбирается определённый тип парсинга.
    # смотреть -> parsing.Parsing.parse()
    SITE_CHOICES = (
        ('https://www.newsru.co.il', 'https://www.newsru.co.il'),  # 1
        ('https://news.israelinfo.co.il', 'https://news.israelinfo.co.il'),  # 2
        ('https://mignews.com', 'https://mignews.com'),  # 3

        ('https://www.jpost.com', 'https://www.jpost.com'),  # 4
        ('https://en.globes.co.il', 'https://en.globes.co.il'),  # 5

        ('https://www.ynet.co.il', 'https://www.ynet.co.il'),  # 6
        ('https://www.mako.co.il', 'https://www.mako.co.il'),  # 7
        ('https://www.globes.co.il', 'https://www.globes.co.il'),  # 8
        ('https://passportnews.co.il', 'https://passportnews.co.il'),  # 9
        ('https://mobile.mako.co.il', 'https://mobile.mako.co.il'),  # 10
        ('https://www.ynet.co.il/tags', 'https://www.ynet.co.il/tags'),  # 11

        ('https://www.ynetnews.com', 'https://www.ynetnews.com')  # 12
    )
    category = peewee.ForeignKeyField(Category, on_delete='CASCADE', backref='urls', null=True)
    site = peewee.CharField(max_length=255, choices=SITE_CHOICES)
    url = peewee.CharField(max_length=255)


class LastPost(BaseModel):
    news = peewee.ForeignKeyField(News, unique=True, on_delete='CASCADE', backref='last_post')
    post_url = peewee.TextField(null=True)


class TGUser(BaseModel):
    LANGUAGE_CHOICES = (
        ('ru', 'ru'),
        ('en', 'en'),
        ('he', 'he'),
    )
    TIME_TO_MAIL = (
        ('morning', 'morning'),
        ('evening', 'evening'),
        ('upon_receipt_of', 'upon_receipt_of'),
    )

    user_id = peewee.IntegerField()
    username = peewee.CharField(max_length=255, null=True)
    phone_number = peewee.CharField(max_length=255, null=True)

    language = peewee.CharField(max_length=3, null=True, choices=LANGUAGE_CHOICES)

    subscribed = peewee.ManyToManyField(Category, on_delete='CASCADE', backref='users')
    time_to_mail = peewee.CharField(max_length=30, choices=TIME_TO_MAIL, default='upon_receipt_of')

    blocked_by_user = peewee.BooleanField(default=False)


class Channel(BaseModel):
    LANGUAGE_CHOICES = (
        ('ru', 'ru'),
        ('en', 'en'),
        ('he', 'he'),
    )

    channel_id = peewee.BigIntegerField()
    channel_url = peewee.CharField(max_length=255)
    channel_title = peewee.CharField(max_length=255)
    language = peewee.CharField(max_length=3, null=True, choices=LANGUAGE_CHOICES)


class Article(BaseModel):
    url = peewee.TextField()
    category = peewee.ForeignKeyField(Category, on_delete='CASCADE', backref='articles')


class Video(BaseModel):
    LANGUAGE_CHOICES = (
        ('ru', 'ru'),
        ('en', 'en'),
        ('he', 'he'),
    )
    TYPE_CHOICES = (
        (1, 1),
        (2, 2)
    )

    video_id = peewee.CharField(max_length=255, null=True)
    video_path = peewee.CharField(max_length=255, null=True)
    video_type = peewee.CharField(max_length=10, choices=TYPE_CHOICES)

    title = peewee.CharField(max_length=255, null=True)
    language = peewee.CharField(max_length=2, choices=LANGUAGE_CHOICES)


class InfoArticle(BaseModel):
    LANGUAGE_CHOICES = (
        ('ru', 'ru'),
        ('en', 'en'),
        ('he', 'he'),
    )

    title = peewee.CharField(max_length=255)
    language = peewee.CharField(max_length=2, choices=LANGUAGE_CHOICES)
    url = peewee.TextField()


class Post(BaseModel):
    TIME_CHOICES = (
        ('morning', 'Утром'),
        ('evening', 'Вечером')
    )
    STATUS_CHOICES = (
        ('accepted', 'Одобрено'),
        ('declined', 'Отказано'),
        ('processing', 'В процессе'),
        ('not_paid', 'Не оплачено'),
        ('posted', 'Выложен')
    )

    user = peewee.ForeignKeyField(TGUser, backref='posts')
    channel = peewee.ForeignKeyField(Channel, backref='posts')
    payment_address = peewee.ForeignKeyField(PaymentAddress, unique=True, backref='post')

    title = peewee.CharField(default='', max_length=255)
    text = peewee.TextField(default='')
    button = peewee.CharField(max_length=255, null=True)
    image_id = peewee.CharField(max_length=255, null=True)  # file_id - from telegram

    date = peewee.DateField('%d.%m.%Y')
    time = peewee.CharField(default='morning', max_length=7, choices=TIME_CHOICES)
    paid = peewee.BooleanField(default=False)

    status = peewee.CharField(max_length=10, choices=STATUS_CHOICES, default='not_paid')
    status_message = peewee.TextField(default='')

    bgcolor = peewee.CharField(max_length=255)  # для админ панели

    created = peewee.DateTimeField()
    updated = peewee.DateTimeField()

    def get_date(self) -> str:
        return self.date.strftime('%d.%m.%Y')

    @property
    def get_time(self) -> str:
        return dict(Post.TIME_CHOICES).get(self.time)

    @property
    def get_status(self) -> str:
        return dict(Post.STATUS_CHOICES).get(self.status)

    def _is_button(self) -> str:
        return self.button

    @property
    def button_text(self) -> str:
        if self._is_button():
            return self.button.split(' - ')[0]  # текст на кнопке

    @property
    def button_url(self) -> Optional[str]:
        if self._is_button():
            return self.button.split(' - ')[1]  # ссылка кнопки

    def get_image(self) -> Optional[str]:
        if self.image_id not in ['', None, False]:
            return self.image_id

    def get_states_data(self) -> dict:
        data = {
            'channel_id': self.channel.id,
            'image_id': self.get_image(),
            'title': self.title,
            'text': self.text,
            'button': self.button,
            'date': self.date,
            'time': self.time
        }
        return data

    async def update_data(self, data: Dict[str, str]) -> None:
        self.title = data.get('title')
        self.text = data.get('text')
        self.button = data.get('button')
        self.image_id = data.get('image_id')
        self.date = data.get('date')
        self.time = data.get('time')
        self.bgcolor = data.get('bgcolor')
        self.updated = data.get('updated')
        self.status = data.get('status')
        self.status_message = data.get('status_message')
        await objects.update(self, list(data.keys()))


category_users_through = Category.users.get_through_model()
