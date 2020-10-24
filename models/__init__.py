from typing import Optional
from .models import (
    objects, Post, User, Category, Channel, category_users_through, URL, InfoArticle, LastPost, Article
)


def setup():
    if not Category.table_exists():
        Category.create_table()
        categories = [
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

        for category, ru_category in zip(categories, ru_categories):
            Category.create(
                key=category,
                name=ru_category,
                language='ru'
            )
        for category, en_category in zip(categories, en_categories):
            Category.create(
                key=category,
                name=en_category,
                language='en'
            )
        for category, he_category in zip(categories, he_categories):
            Category.create(
                key=category,
                name=he_category,
                language='he'
            )

    if not URL.table_exists():
        URL.create_table()

        def create(category: Optional[str], language: Optional[str], site: Optional[str], url: Optional[str]):
            URL.create(
                category=Category.select().where(Category.key == category, Category.language == language).get(),
                site=site,
                url=url
            )

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

    if not Channel.table_exists():
        Channel.create_table()

    if not Post.table_exists():
        Post.create_table()

    if not category_users_through.table_exists():
        category_users_through.create_table()

    if not Article.table_exists():
        Article.create_table()

    if not InfoArticle.table_exists():
        InfoArticle.create_table()

        def info_article_create(title: Optional[str], language: Optional[str], url: Optional[str]):
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
