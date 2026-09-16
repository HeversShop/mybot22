'''Run once locally to generate a Telethon StringSession for the monitor.

1) Get API_ID and API_HASH at https://my.telegram.org -> API development tools
2) pip install telethon
3) TG_API_ID=... TG_API_HASH=... python make_session.py
4) Log in with the phone number of the account that is a MEMBER of @FunPayPlace
5) Copy the printed string into TG_SESSION env of the monitor service.
'''
import os

from telethon.sync import TelegramClient
from telethon.sessions import StringSession

api_id = int(os.getenv('TG_API_ID', '0') or input('API_ID: '))
api_hash = os.getenv('TG_API_HASH', '') or input('API_HASH: ')

with TelegramClient(StringSession(), api_id, api_hash) as client:
    print()
    print('=== YOUR TG_SESSION (keep it secret) ===')
    print(client.session.save())
    print('========================================')
