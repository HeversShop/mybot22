'''aiohttp server: robust mini-app order delivery via /api/order.
Validates Telegram WebApp initData and pushes the order to the bot chat.'''
import hmac
import hashlib
import json
import os
import logging
from urllib.parse import parse_qsl

from aiohttp import web

from config import BOT_TOKEN, WEBAPP_ORIGIN, PORT, ADMIN_IDS
from orders import send_order_from_raw
from common import esc
import database as db

log = logging.getLogger(__name__)


def _cors(resp):
    resp.headers['Access-Control-Allow-Origin'] = WEBAPP_ORIGIN
    resp.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
    resp.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return resp


def validate_init_data(init_data, token):
    '''Verify Telegram WebApp initData. Returns parsed dict or None.'''
    if not init_data or not token:
        return None
    try:
        pairs = dict(parse_qsl(init_data, keep_blank_values=True))
    except Exception:
        return None
    received = pairs.pop('hash', None)
    if not received:
        return None
    data_check_string = '\n'.join(
        k + '=' + pairs[k] for k in sorted(pairs.keys())
    )
    secret_key = hmac.new(b'WebAppData', token.encode(), hashlib.sha256).digest()
    calc = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(calc, received):
        return None
    return pairs


WEBAPP_HTML = None
_here = os.path.dirname(os.path.abspath(__file__))
for _p in (os.path.join(_here, 'webapp', 'index.html'), 'webapp/index.html', 'index.html'):
    try:
        if os.path.exists(_p):
            WEBAPP_HTML = open(_p, encoding='utf-8').read()
            # Serve the mini-app from this very server -> talk to the same origin.
            WEBAPP_HTML = WEBAPP_HTML.replace(
                "const API_BASE='';",
                "const API_BASE=(location.protocol==='https:'?location.origin:'');", 1)
            break
    except Exception:
        pass


async def handle_root(request):
    if WEBAPP_HTML:
        return _cors(web.Response(text=WEBAPP_HTML, content_type='text/html'))
    return _cors(web.Response(text='Oncedshop API OK'))


async def handle_health(request):
    return _cors(web.Response(text='Oncedshop API OK'))


async def handle_options(request):
    return _cors(web.Response(status=204))


async def handle_order(request):
    bot = request.app.get('bot')
    if bot is None:
        return _cors(web.json_response({'ok': False, 'error': 'bot_unavailable'}, status=503))
    try:
        body = await request.json()
    except Exception:
        return _cors(web.json_response({'ok': False, 'error': 'bad_json'}, status=400))

    init_data = body.get('initData') or ''
    order = body.get('order')
    parsed = validate_init_data(init_data, BOT_TOKEN)
    if parsed is None:
        return _cors(web.json_response({'ok': False, 'error': 'bad_init_data'}, status=403))

    try:
        user = json.loads(parsed.get('user', '{}'))
        user_id = int(user.get('id'))
    except Exception:
        return _cors(web.json_response({'ok': False, 'error': 'no_user'}, status=400))

    lang = 'ru'
    if isinstance(order, dict) and order.get('lang') in ('ru', 'en'):
        lang = order['lang']
    raw = order if isinstance(order, (dict, list)) else (order or '')
    try:
        order_id = await send_order_from_raw(bot, user_id, user_id, raw, lang)
    except Exception as e:
        log.exception('api order failed: %s', e)
        return _cors(web.json_response({'ok': False, 'error': 'server'}, status=500))

    if not order_id:
        return _cors(web.json_response({'ok': False, 'error': 'rejected'}, status=422))
    return _cors(web.json_response({'ok': True, 'order_id': order_id}))


async def handle_me(request):
    '''Return the user's balance and personal discount for the mini-app cabinet.'''
    try:
        body = await request.json()
    except Exception:
        return _cors(web.json_response({'ok': False, 'error': 'bad_json'}, status=400))
    parsed = validate_init_data(body.get('initData') or '', BOT_TOKEN)
    if parsed is None:
        return _cors(web.json_response({'ok': False, 'error': 'bad_init_data'}, status=403))
    try:
        user = json.loads(parsed.get('user', '{}'))
        user_id = int(user.get('id'))
    except Exception:
        return _cors(web.json_response({'ok': False, 'error': 'no_user'}, status=400))
    try:
        bal = await db.get_balance(user_id)
        disc = await db.get_discount(user_id)
    except Exception:
        bal, disc = 0.0, 0.0
    return _cors(web.json_response({'ok': True, 'balance': bal, 'discount': disc}))


async def handle_topup(request):
    '''Register a balance top-up request and notify admins to credit it manually.'''
    bot = request.app.get('bot')
    try:
        body = await request.json()
    except Exception:
        return _cors(web.json_response({'ok': False, 'error': 'bad_json'}, status=400))
    parsed = validate_init_data(body.get('initData') or '', BOT_TOKEN)
    if parsed is None:
        return _cors(web.json_response({'ok': False, 'error': 'bad_init_data'}, status=403))
    try:
        user = json.loads(parsed.get('user', '{}'))
        user_id = int(user.get('id'))
        uname = user.get('username') or ''
    except Exception:
        return _cors(web.json_response({'ok': False, 'error': 'no_user'}, status=400))
    try:
        amount = float(body.get('amount') or 0)
    except Exception:
        amount = 0.0
    coin = str(body.get('coin') or '').upper()[:16]
    who = ('@' + uname) if uname else ('id' + str(user_id))
    note = ('💳 <b>Запрос на пополнение баланса</b>' + '\n' +
            'Клиент: ' + esc(who) + ' · id<code>' + str(user_id) + '</code>' + '\n' +
            'Сумма: $' + format(amount, '.2f') + '\n' +
            'Монета: ' + esc(coin or '—') + '\n\n' +
            'После получения оплаты: <code>/balance ' + str(user_id) + ' +' + format(amount, '.2f') + '</code>')
    if bot is not None:
        try:
            from support import notify_staff
            await db.upsert_user(user_id, uname, user.get('first_name') or '')
            await db.ticket_touch(user_id, 'in', 'Пополнение баланса $' + format(amount, '.2f') + ' ' + coin)
            await notify_staff(bot, note, user_id=user_id)
        except Exception as e:
            log.warning('topup notify failed: %s', e)
    return _cors(web.json_response({'ok': True}))


async def handle_status(request):
    bot = request.app.get('bot')
    return _cors(web.json_response({
        'token_set': bool(BOT_TOKEN),
        'bot_ready': bot is not None,
        'bot_username': request.app.get('bot_me'),
        'admins': len(ADMIN_IDS),
        'webapp_loaded': bool(WEBAPP_HTML),
    }))


def build_app(bot):
    app = web.Application()
    app['bot'] = bot
    app.router.add_get('/', handle_root)
    app.router.add_get('/api/health', handle_health)
    app.router.add_get('/status', handle_status)
    app.router.add_get('/api/status', handle_status)
    app.router.add_get('/api/order', handle_health)
    app.router.add_options('/api/order', handle_options)
    app.router.add_post('/api/order', handle_order)
    app.router.add_options('/api/me', handle_options)
    app.router.add_post('/api/me', handle_me)
    app.router.add_options('/api/topup', handle_options)
    app.router.add_post('/api/topup', handle_topup)
    return app


async def start_webserver(bot):
    '''Start aiohttp server on 0.0.0.0:PORT and return the runner.'''
    app = build_app(bot)
    if bot is not None:
        try:
            me = await bot.get_me()
            app['bot_me'] = me.username
            log.info('Bot authorized as @%s', me.username)
        except Exception as e:
            app['bot_me'] = None
            log.exception('bot.get_me failed (check BOT_TOKEN): %s', e)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', PORT)
    await site.start()
    log.info('Web server started on :%s', PORT)
    return runner
