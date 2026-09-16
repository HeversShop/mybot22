'''Shared order processing: build + deliver order with payment options.
Used by both the WebApp service message (sendData) and the HTTP API.'''
import json
import logging

from config import MIN_ORDER_USD, USD_TO_RUB
from catalog import find_product
from utils import (
    with_markup, unit_price, price_per_1000, generate_order_id, tt, format_money, get_usd_rub,
)
import database as db
from keyboards import payment_kb

log = logging.getLogger(__name__)
NL = chr(10)

# In-memory pending orders for the payment step: {order_id: {...}}
PENDING = {}


def R(lang):
    return lang == 'ru'


def money(usd, currency='USD', rate=None):
    return format_money(usd, currency, rate)


async def build_order(user_id, raw, lang_default='ru'):
    '''Parse raw JSON order, price it, persist it. Returns (ok, result).'''
    if isinstance(raw, (dict, list)):
        data = raw
        raw_str = json.dumps(raw, ensure_ascii=False)
    else:
        raw_str = raw or ''
        try:
            data = json.loads(raw_str)
        except Exception:
            return False, {'lang': lang_default,
                           'error_text': '⚠️ Не удалось прочитать заказ.'}

    lang = data.get('lang') or lang_default or 'ru'
    if lang not in ('ru', 'en'):
        lang = 'ru'

    currency = str(data.get('currency') or 'USD').upper()
    if currency not in ('USD', 'RUB'):
        currency = 'USD'

    rate = float(data.get('rate') or 0) or await get_usd_rub()
    if rate < 1:
        rate = float(USD_TO_RUB)

    items = data.get('items') or []
    if not items:
        return False, {'lang': lang, 'error_text': ('Корзина пуста.' if R(lang) else 'Cart is empty.')}

    total = 0.0
    lines = []
    for it in items:
        p = find_product(it.get('id', ''))
        if not p:
            continue
        if p.get('kind') == 'per1000':
            qty = int(it.get('qty', 0) or 0)
            amount = price_per_1000(p, qty)
        else:
            qty = int(it.get('qty', 1) or 1)
            amount = round(unit_price(p) * qty, 2)
        total += amount
        lines.append((tt(p['title'], lang), qty, p.get('unit', ''), amount, p))
    total = round(total, 2)

    # Personal per-user discount (set by admin)
    disc_pct = 0.0
    try:
        disc_pct = float(await db.get_discount(user_id) or 0)
    except Exception:
        disc_pct = 0.0
    disc_amount = 0.0
    if disc_pct > 0:
        disc_amount = round(total * disc_pct / 100.0, 2)
        total = round(total - disc_amount, 2)

    if not lines:
        return False, {'lang': lang, 'error_text': ('Товары не найдены.' if R(lang) else 'Products not found.')}

    if total < MIN_ORDER_USD:
        msg = (('Минимальный заказ — $' + str(int(MIN_ORDER_USD)) +
                ' (~' + str(int(MIN_ORDER_USD * rate)) + ' ₽). Ваш итог: ' +
                money(total, 'USD', rate) + ' / ' + money(total, 'RUB', rate) + '.')
               if R(lang) else
               ('Minimum order is $' + str(int(MIN_ORDER_USD)) +
                ' (~' + str(int(MIN_ORDER_USD * rate)) + ' ₽). Your total: ' +
                money(total, 'USD', rate) + ' / ' + money(total, 'RUB', rate) + '.'))
        return False, {'lang': lang, 'error_text': msg}

    order_id = generate_order_id()
    contact = str(data.get('contact') or '').strip()
    rows = []
    rows.append(('🧾 <b>Заказ</b> <code>' + order_id + '</code>') if R(lang)
                else ('🧾 <b>Order</b> <code>' + order_id + '</code>'))
    rows.append('')
    notes = []
    for title, qty, unit, amount, p in lines:
        if p.get('kind') == 'per1000':
            rows.append('• ' + title + ' — ' + str(qty) + ' ' + unit + ' = ' + money(amount, currency, rate))
        else:
            rows.append('• ' + title + ' ×' + str(qty) + ' = ' + money(amount, currency, rate))
        if p.get('note'):
            notes.append('— ' + title + ': ' + tt(p['note'], lang))
    rows.append('')
    if disc_pct > 0:
        rows.append((('🏷 Персональная скидка −' + format(disc_pct, '.0f') + '%  (−' + money(disc_amount, 'USD', rate) + ')')
                     if R(lang) else
                     ('🏷 Personal discount −' + format(disc_pct, '.0f') + '%  (−' + money(disc_amount, 'USD', rate) + ')')))
    rows.append(('<b>Итого: </b>' if R(lang) else '<b>Total: </b>') +
                money(total, 'USD', rate) + '  ·  ' + money(total, 'RUB', rate))
    rows.append(('Курс: 1$ ≈ ' + format(rate, '.2f') + ' ₽') if R(lang)
                else ('Rate: 1$ ≈ ' + format(rate, '.2f') + ' ₽'))
    if contact:
        rows.append((('Контакт: ') if R(lang) else 'Contact: ') + '<code>' + contact + '</code>')
    if notes:
        rows.append('')
        rows.append('ℹ️ ' + ('Выдача:' if R(lang) else 'Delivery:'))
        rows.extend(notes)
    rows.append('')
    rows.append('Выберите способ оплаты:' if R(lang) else 'Choose a payment method:')

    await db.create_order({
        'order_id': order_id,
        'user_id': user_id,
        'product_id': ','.join([p['id'] for (_, _, _, _, p) in lines]),
        'title': '; '.join([t + ' x' + str(q) for (t, q, _, _, _) in lines]),
        'quantity': len(lines),
        'amount_usd': total,
        'account': contact,
        'details': raw_str,
        'status': 'created',
    })
    PENDING[order_id] = {
        'total': total, 'user_id': user_id, 'lang': lang,
        'currency': currency, 'rate': rate,
    }
    return True, {'lang': lang, 'order_id': order_id, 'text': NL.join(rows)}


async def send_order_from_raw(bot, chat_id, user_id, raw, lang_default='ru'):
    '''Build the order and send it to chat_id with payment buttons.'''
    ok, res = await build_order(user_id, raw, lang_default)
    lang = res.get('lang', lang_default)
    if not ok:
        await bot.send_message(chat_id, res['error_text'])
        return None
    await bot.send_message(chat_id, res['text'], reply_markup=payment_kb(res['order_id'], lang))
    return res['order_id']
