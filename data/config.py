from decouple import config as env

from pathlib import Path

import json


# BOT settings
BOT_TOKEN = env('BOT_TOKEN')
BOT_USERNAME = env('BOT_USERNAME')

# WEB settings
BASE_URL = env('WEBHOOK_DOMAIN')  # Webhook domain
WEBHOOK_PATH = f'/tg/webhooks/bot/{BOT_TOKEN}'
WEBHOOK_URL = f'{BASE_URL}{WEBHOOK_PATH}'

# BTC settings
BTC_WALLET_ID = env('BTC_WALLET_ID')
BTC_WALLET_ID_HASH = env('BTC_WALLET_ID_HASH')
BTC_CALLBACK_LINK = env('BTC_CALLBACK_LINK')

# PATH settings
BASE_DIR = Path(__file__).parent.parent
LOGS_BASE_PATH = str(BASE_DIR / 'logs')

# I18N settings
I18N_DOMAIN = 'foxy'
LOCALES_DIR = BASE_DIR / 'locales'

# TIMEZONE settings
TIMEZONE = env('TIMEZONE')

# ADMIN settings
ADMINS = {
    'foxy': 414908999,
    'kolyabjj': 1092694232
}

ip = {
    'db':    '127.0.0.1',
    'redis': 'redis://localhost',
}

postgresql_info = {
    'host':     ip['db'],
    'user':     'postgres',
    'password': '',
    'db':       'foxy',
}

mysql = {
    'host': ip['db'],
    'user': 'root',
    'password': '123root123',
    'db': 'test'
}

redis = {
    'host': ip['redis'],
    'password': ''
}

with open('data/messages.json', 'r', encoding='utf-8') as fp:
    messages = json.load(fp)
