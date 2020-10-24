from data import config

import peewee
from peewee_async import MySQLDatabase, Manager


database = MySQLDatabase(
    config.mysql_info['db'],
    user=config.mysql_info['user'],
    password=config.mysql_info['password'],
    host=config.mysql_info['host']
)

objects = Manager(database)


class BaseModel(peewee.Model):
    class Meta:
        database = database


class Category(BaseModel):
    key = peewee.CharField(max_length=255)
    name = peewee.CharField(max_length=255)
    language = peewee.CharField(max_length=2)
    is_active = peewee.BooleanField(default=True)


class URL(BaseModel):
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
        ('https://www.ynet.co.il/tags/', 'https://www.ynet.co.il/tags/')  # 11
    )
    category = peewee.ForeignKeyField(Category, on_delete='CASCADE', backref='urls', null=True)
    site = peewee.CharField(max_length=255, choices=SITE_CHOICES)
    url = peewee.CharField(max_length=255)


class LastPost(BaseModel):
    category = peewee.ForeignKeyField(Category, unique=True, on_delete='CASCADE', backref='last_posts')
    url = peewee.TextField()


class User(BaseModel):
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
    user_phone = peewee.CharField(max_length=255, null=True)

    lang = peewee.CharField(max_length=3, null=True, choices=LANGUAGE_CHOICES)

    btc_address_to_pay = peewee.CharField(max_length=255, null=True)

    subscribed = peewee.ManyToManyField(Category, on_delete='CASCADE', backref='users')
    time_to_mail = peewee.CharField(max_length=30, choices=TIME_TO_MAIL, default='upon_receipt_of')

    ru_subscribed = peewee.BooleanField(default=False)
    en_subscribed = peewee.BooleanField(default=False)
    he_subscribed = peewee.BooleanField(default=False)


class ChannelAdmin(BaseModel):
    LANGUAGE_CHOICES = (
        ('ru', 'ru'),
        ('en', 'en'),
        ('he', 'he'),
    )

    channel_id = peewee.BigIntegerField()
    channel_url = peewee.CharField(max_length=255)
    language = peewee.CharField(max_length=3, null=True, choices=LANGUAGE_CHOICES)


class Article(BaseModel):
    url = peewee.TextField()
    category = peewee.ForeignKeyField(Category, on_delete='CASCADE', backref='articles')


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
        ('not_paid', 'Не оплачено')
    )

    user = peewee.ForeignKeyField(User, related_name='posts')

    uuid_pay = peewee.UUIDField(null=True)

    title = peewee.CharField(null=True, max_length=255)
    text = peewee.TextField(null=True)
    button = peewee.CharField(max_length=255, null=True)
    image_id = peewee.CharField(max_length=255, null=True)  # file_id - from telegram

    date = peewee.DateField('%d.%m.%Y')
    time = peewee.CharField(default='morning', max_length=7, choices=TIME_CHOICES)
    paid = peewee.BooleanField(default=False)

    status = peewee.CharField(max_length=10, choices=STATUS_CHOICES, default='not_paid')
    status_message = peewee.TextField(null=True)

    bgcolor = peewee.CharField(max_length=255)  # для админ панели

    created = peewee.DateTimeField()

    @property
    def get_time(self):
        return dict(Post.TIME_CHOICES).get(self.time)

    @property
    def get_status(self):
        return dict(Post.STATUS_CHOICES).get(self.status)

    def _is_button(self) -> str or None:
        return self.button

    @property
    def button_text(self) -> str:
        if self._is_button():
            return self.button.split(' - ')[0]  # текст на кнопке

    @property
    def button_url(self) -> str:
        if self._is_button():
            return self.button.split(' - ')[1]  # ссылка кнопки


category_users_through = Category.users.get_through_model()
