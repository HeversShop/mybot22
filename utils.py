'''Pricing and helper utilities for Oncedshop.'''
import json
import secrets
import time
import urllib.request
from config import PRICE_MARKUP, USD_TO_RUB, STARS_PER_RUB

_RATE_CACHE = {'rate': float(USD_TO_RUB), 'ts': 0.0}
_RATE_TTL = 3600.0


def with_markup(usd):
    return round(usd * (1 + PRICE_MARKUP), 2)


def unit_price(product):
    '''Final per-unit USD price for a fixed product.
    If the product sets an explicit "price" (e.g. discounted gift cards), use it
    as-is; otherwise apply the standard markup to "base".'''
    if product.get('price') is not None:
        return round(float(product['price']), 2)
    return with_markup(product['base'])


def discount_pct(product):
    '''Percent below official price for products that declare a "face" value.'''
    face = product.get('face')
    if not face:
        return 0
    price = unit_price(product)
    if price >= face:
        return 0
    return int(round((1 - price / float(face)) * 100))


def rate_per_1000(product, units):
    tier_u = product.get('tier_units')
    if tier_u and units >= tier_u:
        return product['tier_rate']
    return product['base']


def price_per_1000(product, units):
    rate = rate_per_1000(product, units)
    return round(units / 1000 * rate * (1 + PRICE_MARKUP), 2)


def min_line(product):
    if product.get('kind') == 'per1000':
        return max(with_markup(product.get('min', 0)), 0.0)
    return 0.0


def usd_to_stars(usd, rate=None):
    r = float(rate if rate is not None else USD_TO_RUB)
    return max(1, round(usd * r * STARS_PER_RUB))


def crypto_amount(usd, unit_usd, dp):
    amt = (usd / unit_usd) if unit_usd else 0.0
    return format(amt, '.' + str(dp) + 'f')


def generate_order_id():
    return 'ONC-' + secrets.token_hex(4).upper()


def tt(value, lang):
    if isinstance(value, dict):
        return value.get(lang) or value.get('ru') or ''
    return value


def format_money(usd, currency='USD', rate=None):
    r = float(rate if rate is not None else USD_TO_RUB)
    cur = (currency or 'USD').upper()
    if cur == 'RUB':
        rub = round(float(usd or 0.0) * r)
        return str(rub) + ' ₽'
    return '$' + format(round(float(usd or 0.0), 2), '.2f')


def _fetch_rate_sync():
    sources = [
        ('https://open.er-api.com/v6/latest/USD', 'er'),
        ('https://api.frankfurter.app/latest?from=USD&to=RUB', 'ff'),
        ('https://www.cbr-xml-daily.ru/daily_json.js', 'cbr'),
    ]
    for url, kind in sources:
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Oncedshop/1.0'})
            with urllib.request.urlopen(req, timeout=8) as resp:
                data = json.loads(resp.read().decode('utf-8'))
            if kind == 'er':
                rate = float(data['rates']['RUB'])
            elif kind == 'ff':
                rate = float(data['rates']['RUB'])
            else:
                rate = float(data['Valute']['USD']['Value'])
            if rate > 1:
                return rate
        except Exception:
            continue
    return float(USD_TO_RUB)


async def get_usd_rub(force=False):
    now = time.time()
    if (not force) and _RATE_CACHE['rate'] and (now - _RATE_CACHE['ts'] < _RATE_TTL):
        return float(_RATE_CACHE['rate'])
    import asyncio
    rate = await asyncio.to_thread(_fetch_rate_sync)
    _RATE_CACHE['rate'] = float(rate)
    _RATE_CACHE['ts'] = now
    return float(rate)

# ---- Assortment / lead matching (for chat monitor) ----
ASSORTMENT_KEYWORDS = [
    'telegram stars', 'stars', 'звёзды', 'звезды', 'звезд',
    'brawl', 'brawl pass', 'бравл',
    'gemini', 'гемини', 'google ai', 'chatgpt', 'chat gpt', 'gpt', 'чат гпт', 'гпт',
    'claude', 'клод', 'grok', 'грок', 'x premium', 'икс премиум', 'premium',
    'robux', 'робукс', 'роблокс', 'roblox', 'gamepass', 'game pass', 'гейм пасс',
]


def _norm(s):
    return (s or '').lower().replace('ё', 'е')


def match_assortment(text):
    t = _norm(text)
    found = []
    for k in ASSORTMENT_KEYWORDS:
        if _norm(k) in t and k not in found:
            found.append(k)
    return found


def match_triggers(text, triggers):
    t = _norm(text)
    return [w for w in triggers if _norm(w) in t]
