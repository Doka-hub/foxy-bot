from decouple import config as env

from pathlib import Path

import json


BOT_TOKEN = env('BOT_TOKEN')
BASE_URL = env('WEBHOOK_DOMAIN')  # Webhook domain
WEBHOOK_PATH = f'/tg/webhooks/bot/{BOT_TOKEN}'
WEBHOOK_URL = f'{BASE_URL}{WEBHOOK_PATH}'
BTC_WALLET_ID = env('BTC_WALLET_ID')

LOGS_BASE_PATH = str(Path(__file__).parent.parent / 'logs')

admins = {
    'foxy': 414908999,
    'kolyabjj': 1092694232
}

ip = {
    'db':    '127.0.0.1',
    'redis': 'localhost',
}

postgresql_info = {
    'host':     ip['db'],
    'user':     'postgres',
    'password': '',
    'db':       'foxy',
}

redis = {
    'host': ip['redis'],
    'password': ''
}

with open('data/messages.json', 'r', encoding='utf-8') as fp:
    messages = json.load(fp)
