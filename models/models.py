import peewee
from peewee_async import MySQLDatabase, Manager


database = MySQLDatabase(
    'test',
    user='root',
    password='123riko123',
    host='localhost'
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


if __name__ == '__main__':

    # проверка наличия таблиц; создание категорий и ссылок для парсинга
    if not Category.table_exists():
        Category.create_table()
        keys = [
            'health', 'economic', 'politic', 'world', 'science_and_technology', 'realty', 'cars', 'conflicts',
            'sport', 'USA_and_Canada', 'travel', 'culture', 'incidents'
        ]

        ru_categories = [
            'Здоровье', 'Экономика', 'Политика', 'В_мире', 'Наука_и_технологии', 'Недвижимость', 'Машины', 'Конфликты',
            'Спорт', 'США_и_Канада', 'Путешествия', 'Культура', 'Происшествия'
        ]
        en_categories = [
            'Health', 'Economy', 'Politic', 'World', 'Science_and_technology', 'Realty', 'Cars', 'Conflicts',
            'Sport', 'USA_and_Canada', 'Travel', 'Culture', 'Incidents'
        ]
        he_categories = [
            'בריאות', 'כלכלה', 'פוליטי', 'בעולם', 'טכנולוגיה', 'נדל“ן', 'רכב', 'עימותים_צבאיים',
            'ספורט', 'ארה"ב_וקנדה', 'תיירות', 'תרבות', 'תאונות'
        ]

        for key, category in zip(keys, ru_categories):
            Category.create(
                key=key,
                name=category,
                language='ru'
            )
        for key, category in zip(keys, en_categories):
            Category.create(
                key=key,
                name=category,
                language='en'
            )
        for key, category in zip(keys, he_categories):
            Category.create(
                key=key,
                name=category,
                language='he'
            )

    if not URL.table_exists():
        URL.create_table()


        def create(category, language, site, url):
            URL.create(
                category=Category.select().where(Category.key == category, Category.language == language).get(),
                site=site,
                url=url
            )


        # {язык :
        #   {категория:
        #       [
        #           (тип сайта (для парсинга), ссылка)
        #       ]
        #   }
        # }
        urls = {
            'ru':
                {
                    'health':
                        [
                            ('https://www.newsru.co.il', 'https://www.newsru.co.il/health/'),
                            ('https://news.israelinfo.co.il', 'https://news.israelinfo.co.il/health/')
                        ],
                    'economic':
                        [
                            ('https://news.israelinfo.co.il', 'https://news.israelinfo.co.il/economy/'),
                            ('https://mignews.com', 'https://mignews.com/news/economics/')
                        ],
                    'politic':
                        [
                            ('https://mignews.com', 'https://mignews.com/news/politic/')
                        ],
                    'world':
                        [
                            ('https://www.newsru.co.il', 'https://www.newsru.co.il/world/'),
                            ('https://news.israelinfo.co.il', 'https://news.israelinfo.co.il/world/')
                        ],
                    'science_and_technology':
                        [
                            ('https://news.israelinfo.co.il', 'https://news.israelinfo.co.il/technology/'),
                            ('https://mignews.com', 'https://mignews.com/news/technology')
                        ],
                    'realty':
                        [
                            ('https://www.newsru.co.il', 'https://www.newsru.co.il/realty/')
                        ],
                    'cars':
                        [
                            ('https://www.newsru.co.il', 'https://www.newsru.co.il/auto/')
                        ],
                    'conflicts':
                        [
                            ('https://mignews.com', 'https://mignews.com/news/arabisrael/'),
                            ('https://www.newsru.co.il', 'https://www.newsru.co.il/mideast/')
                        ],
                    'sport':
                        [
                            ('https://www.newsru.co.il', 'https://www.newsru.co.il/sport/'),
                            ('https://mignews.com', 'https://mignews.com/news/sport')
                        ],
                    'USA_and_Canada':
                        [
                            ('https://mignews.com', 'https://mignews.com/news/USACANADA/')
                        ],
                    'travel':
                        [
                            ('https://mignews.com', 'https://mignews.com/news/travel/')
                        ],
                    'culture':
                        [
                            ('https://mignews.com', 'https://mignews.com/news/culture/')
                        ],
                    'incidents':
                        [
                            ('https://news.israelinfo.co.il', 'https://news.israelinfo.co.il/events/')
                        ]
                },
            'en':
                {
                    'health':
                        [
                            ('https://www.jpost.com', 'https://www.jpost.com/health-science'),
                            ('https://en.globes.co.il', 'https://en.globes.co.il/en/healthcare.tag')
                        ],
                    'economic':
                        [
                            ('https://en.globes.co.il', 'https://en.globes.co.il/en/economy.tag')
                        ],
                    'politic':
                        [
                            ('https://www.jpost.com', 'https://www.jpost.com/israel-news/politics-and-diplomacy'),
                            ('https://en.globes.co.il', 'https://en.globes.co.il/en/politics.tag')
                        ],
                    'world':
                        [
                            ('https://www.jpost.com', 'https://www.jpost.com/international')
                        ],
                    'science_and_technology':
                        [
                            ('https://www.jpost.com', 'https://www.jpost.com/cybertech'),
                            ('https://www.jpost.com', 'https://www.jpost.com/jpost-tech')
                        ],
                    'realty':
                        [
                            ('https://en.globes.co.il', 'https://en.globes.co.il/en/realestate.tag')
                        ],
                    'cars':
                        [
                            ('https://www.jpost.com', 'https://www.autocar.co.uk/car-news')
                        ],
                    'conflicts':
                        [
                            ('https://www.jpost.com', 'https://www.jpost.com/middle-east'),
                        ],
                    'sport':
                        [
                            ('https://www.jpost.com', 'https://www.jpost.com/israel-news/sports')
                        ],
                    'USA_and_Canada':
                        [
                            ('https://www.jpost.com', 'https://www.jpost.com/american-politics'),
                        ],
                    'travel':
                        [
                            ('https://en.globes.co.il', 'https://en.globes.co.il/en/tourism.tag')
                        ],
                    'culture':
                        [
                            ('https://www.jpost.com', 'https://www.jpost.com/israel-news/culture')
                        ],
                    'incidents':
                        [
                            ('https://www.timesofisrael.com', 'https://www.timesofisrael.com/topic/crime-in-israel'),
                            ('https://jpost.com', 'https://jpost.com/tags/crime'),
                        ]
                },
            'he':
                {
                    'health':
                        [
                            ('https://www.ynet.co.il', 'https://www.ynet.co.il/health/category/4647'),
                        ],
                    'economic':
                        [
                            ('https://www.ynet.co.il', 'https://www.ynet.co.il/economy/category/429'),
                            ('https://www.ynet.co.il', 'https://www.ynet.co.il/economy/category/430'),
                        ],
                    'politic':
                        [
                            ('https://www.mako.co.il', 'https://www.mako.co.il/news-politics?partner=NewsNavBar'),
                        ],
                    'world':
                        [
                            ('https://www.mako.co.il', 'https://www.mako.co.il/news-world?partner=NewsNavBar')
                        ],
                    'science_and_technology':
                        [
                            ('https://www.ynet.co.il', 'https://www.ynet.co.il/digital/technews/'),
                            ('https://www.mako.co.il', 'https://www.mako.co.il/news-digital?partner=NewsNavBar')
                        ],
                    'realty':
                        [
                            ('https://www.ynet.co.il', 'https://www.ynet.co.il/economy/category/8316')
                        ],
                    'cars':
                        [
                            ('https://www.ynet.co.il', 'https://www.ynet.co.il/wheels/news'),
                            ('https://www.ynet.co.il', 'https://www.ynet.co.il/wheels/safety'),
                        ],
                    'conflicts':
                        [
                            ('https://www.mako.co.il', 'https://www.mako.co.il/news-military?partner=NewsNavBar'),
                        ],
                    'sport':
                        [
                            ('https://www.mako.co.il', 'https://www.mako.co.il/news-sport?partner=NewsNavBar')
                        ],
                    'USA_and_Canada':
                        [
                            ('https://www.ynet.co.il/tags/', 'https://www.ynet.co.il/tags/ארה%22ב'),
                        ],
                    'travel':
                        [
                            ('https://www.globes.co.il', 'https://www.globes.co.il/news/תיירות.tag'),
                            ('https://passportnews.co.il', 'https://passportnews.co.il/תיירות/'),
                            ('https://mobile.mako.co.il', 'https://mobile.mako.co.il/Tagit/קנדה'),
                        ],
                    'culture':
                        [
                            ('https://www.mako.co.il', 'https://www.mako.co.il/news-entertainment?partner=NewsNavBar')
                        ],
                    'incidents':
                        [
                            ('https://www.mako.co.il', 'https://www.mako.co.il/news-law?partner=NewsNavBar'),
                        ]
                }
        }
        for language in urls:
            for category in urls[language]:
                for url in urls[language][category]:
                    create(category, language, site=url[0], url=url[1])

    if not LastPost.table_exists():
        LastPost.create_table()

    if not User.table_exists():
        User.create_table()

    if not Category.users.get_through_model().table_exists():
        Category.users.get_through_model().create_table()

    if not ChannelAdmin.table_exists():
        ChannelAdmin.create_table()

    if not Article.table_exists():
        Article.create_table()

    if not InfoArticle.table_exists():
        InfoArticle.create_table()

        def info_article_create(title: str, language: str, url: str):
            InfoArticle.create(
                title=title,
                language=language,
                url=url
            )

        info_articles = {
            'ru': (
                ('Как купить рекламу?', 'https://google.com'),
                ('Что такое биткоин?', 'https://telegra.ph/CHto-takoe-Bitcoin-10-12-2'),
                ("SAVL. Приватный и Маркет кошельки",
                 'https://telegra.ph/SAVL-CHto-takoe-Privatnyj-koshelek-i-Market-koshelek-Dlya-chego-oni-nuzhny-i-v'
                 '-chem-raznica-10-12'),
                ('SAVL. Как купить криптовалюту?', 'https://telegra.ph/SAVL-Kak-kupit-kriptovalyutu-10-12'),
                ('SAVL. Как продать криптовалюту?', 'https://telegra.ph/SAVL-Kak-prodat-kriptovalyutu-10-12'),
                ('SAVL. Верификация. Как ее пройти?',
                 'https://telegra.ph/SAVL-Dlya-chego-nuzhna-verifikaciya-KYC-i-kak-ee-projti-10-12'),
                ('SAVL. Объявления на покупку/продажу?',
                 'https://telegra.ph/SAVL-Kak-sozdat-obyavlenie-na-pokupku-ili-prodazhu-10-12'),
                ('SAVL. Покупка bitcoin с карты',
                 'https://telegra.ph/SAVL-Kak-kupit-kriptovalyutu-napryamuyu-s-debetovojkreditnoj-karty-ili-s'
                 '-pomoshchyu-Apple-Pay-10-12'),
            ),
            'en': (
                ('How to buy ads?', 'https://google.com'),
                ('What is Bitcoin?', 'https://telegra.ph/What-is-bitcoin-10-12'),
                ('SAVL. What are Private and Market wallets? What are they for and what is the difference between them?',
                 'https://telegra.ph/SAVL-What-are-Private-and-Market-wallets-What-are-they-for-and-what-is-the'
                 '-difference-between-them-10-12'),
                ('SAVL. How can I buy crypto?', 'https://telegra.ph/SAVL-How-can-I-buy-crypto-10-12'),
                ('SAVL. How can I sell crypto?', 'https://telegra.ph/SAVL-How-can-I-sell-crypto-10-12'),
                ('SAVL. Why is the verification (KYC) necessary and how do I complete it?',
                 'https://telegra.ph/SAVL-Why-is-the-verification-KYC-necessary-and-how-do-I-complete-it-10-12'),
                ('SAVL. Why is verification (KYC) necessary and how to get through it?',
                 'https://telegra.ph/SAVL-Why-is-verification-KYC-necessary-and-how-to-get-through-it-10-12'),
                ('SAVL. How can I buy crypto with debit/credit card or Apple Pay?',
                 'https://telegra.ph/SAVL-How-can-I-buy-crypto-with-debitcredit-card-or-Apple-Pay-10-12'),
            ),
            'he': (
                ('כיצד אוכל לקנות מודעות?', 'https://google.com'),
                ('מה זה ביטקוין?',
                 'https://telegra.ph/%D7%9E%D7%94-%D7%96%D7%94-%D7%91%D7%99%D7%98%D7%A7%D7%95%D7%99%D7%9F-10-12'),
                ('SAVL. What are Private and Market wallets? What are they for and what is the difference between them?',
                 'https://telegra.ph/SAVL-What-are-Private-and-Market-wallets-What-are-they-for-and-what-is-the'
                 '-difference-between-them-10-12'),
                ('SAVL. How can I buy crypto?', 'https://telegra.ph/SAVL-How-can-I-buy-crypto-10-12'),
                ('SAVL. How can I sell crypto?', 'https://telegra.ph/SAVL-How-can-I-sell-crypto-10-12'),
                ('SAVL. Why is the verification (KYC) necessary and how do I complete it?',
                 'https://telegra.ph/SAVL-Why-is-the-verification-KYC-necessary-and-how-do-I-complete-it-10-12'),
                ('SAVL. Why is verification (KYC) necessary and how to get through it?',
                 'https://telegra.ph/SAVL-Why-is-verification-KYC-necessary-and-how-to-get-through-it-10-12'),
                ('SAVL. How can I buy crypto with debit/credit card or Apple Pay?',
                 'https://telegra.ph/SAVL-How-can-I-buy-crypto-with-debitcredit-card-or-Apple-Pay-10-12')
            )
        }
        for language in info_articles:
            for title, url in info_articles[language]:
                info_article_create(title, language, url)

    if not Post.table_exists():
        Post.create_table()
