'''Chat monitor (Telethon userbot).

A Telegram BOT cannot read messages from foreign chats/groups, so monitoring
@FunPayPlace requires a real user account (userbot). This script logs in with a
StringSession, watches MONITOR_CHATS, and saves a lead whenever a message
contains one of MONITOR_TRIGGERS AND matches the bot assortment.

Run as a separate process/service:  python monitor.py

Env needed: TG_API_ID, TG_API_HASH, TG_SESSION (StringSession).
Generate a session string once with make_session.py.
'''
import asyncio
import logging
import urllib.parse
import urllib.request

from config import (
    TG_API_ID, TG_API_HASH, TG_SESSION, MONITOR_CHATS, MONITOR_TRIGGERS,
    BOT_TOKEN, ADMIN_IDS, MONITOR_NOTIFY_ADMIN,
)
from utils import match_assortment, match_triggers
import database as db

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s monitor: %(message)s')
log = logging.getLogger('monitor')

try:
    from telethon import TelegramClient, events
    from telethon.sessions import StringSession
except Exception:
    TelegramClient = None
    events = None
    StringSession = None


def _notify_admin(text):
    if not (MONITOR_NOTIFY_ADMIN and BOT_TOKEN and ADMIN_IDS):
        return
    for admin_id in ADMIN_IDS:
        try:
            data = urllib.parse.urlencode({
                'chat_id': admin_id, 'text': text,
                'parse_mode': 'HTML', 'disable_web_page_preview': 'true',
            }).encode()
            url = 'https://api.telegram.org/bot' + BOT_TOKEN + '/sendMessage'
            urllib.request.urlopen(urllib.request.Request(url, data=data), timeout=10)
        except Exception as e:
            log.warning('notify admin failed: %s', e)


async def _handle(event):
    msg = event.message
    text = msg.message or ''
    if not text:
        return
    trig = match_triggers(text, MONITOR_TRIGGERS)
    if not trig:
        return
    matched = match_assortment(text)
    if not matched:
        return
    try:
        sender = await event.get_sender()
        author = getattr(sender, 'username', None) or ''
        author_id = getattr(sender, 'id', None)
    except Exception:
        author, author_id = '', None
    try:
        chat = await event.get_chat()
        chat_name = getattr(chat, 'username', None) or str(getattr(chat, 'id', ''))
    except Exception:
        chat_name = ''
    link = ''
    if chat_name:
        link = 'https://t.me/' + str(chat_name) + '/' + str(msg.id)
    is_new = await db.add_lead({
        'source': 'telegram', 'chat': chat_name, 'message_id': msg.id,
        'author': author, 'author_id': author_id, 'text': text,
        'matched': ', '.join(matched), 'triggers': ', '.join(trig), 'link': link,
        'status': 'new',
    })
    if is_new:
        log.info('LEAD #%s by @%s: %s | %s', msg.id, author, trig, matched)
        who = ('@' + author) if author else ('id' + str(author_id or ''))
        _notify_admin(
            '🆕 <b>Новый лид</b> из @' + chat_name + '\n' +
            who + '\n🔑 ' + ', '.join(trig) + '  ·  🏷 ' + ', '.join(matched) +
            '\n💬 ' + (text[:200]) + ('…' if len(text) > 200 else '') +
            ('\n🔗 ' + link if link else '') + '\n\nОткройте /admin'
        )


async def main():
    if TelegramClient is None:
        raise SystemExit('Telethon is not installed. Run: pip install telethon')
    if not (TG_API_ID and TG_API_HASH and TG_SESSION):
        raise SystemExit('Set TG_API_ID, TG_API_HASH and TG_SESSION (see make_session.py).')
    await db.init_db()
    client = TelegramClient(StringSession(TG_SESSION), TG_API_ID, TG_API_HASH)
    await client.start()
    log.info('Monitor connected. Watching: %s', MONITOR_CHATS)
    log.info('Triggers: %s', MONITOR_TRIGGERS)

    @client.on(events.NewMessage(chats=MONITOR_CHATS))
    async def _on_new(event):
        try:
            await _handle(event)
        except Exception as e:
            log.exception('handle failed: %s', e)

    await client.run_until_disconnected()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        pass
