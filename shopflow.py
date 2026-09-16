'''In-bot shopping: browse, cart and checkout WITHOUT the mini app.
Orders are built by the shared orders.build_order/send_order_from_raw so the
payment step (Stars / crypto / CryptoBot) is identical to the mini-app path.'''
import logging

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from config import MIN_ORDER_USD
from catalog import CATALOG, find_product
from utils import with_markup, unit_price, discount_pct, price_per_1000, min_line, tt, format_money, get_usd_rub
import database as db
from orders import send_order_from_raw
from keyboards import CATALOG_LABELS, CART_LABELS

shop_router = Router()
NL = chr(10)
log = logging.getLogger(__name__)

# In-memory carts and pending custom-quantity prompts.
CART = {}          # user_id -> { pid: units }
PENDING_QTY = {}   # user_id -> pid awaiting a typed amount


def R(lang):
    return lang == 'ru'


def money(usd, currency='USD', rate=None):
    return format_money(usd, currency, rate)


def both(usd, rate):
    return money(usd, 'USD', rate) + ' · ' + money(usd, 'RUB', rate)


def _cat_of(pid):
    for cat in CATALOG:
        for p in cat.get('items', []):
            if p['id'] == pid:
                return cat
    return None


def presets(p):
    if p.get('unit') == 'Stars':
        return [500, 1000, 2500, 5000, 10000]
    return [1000, 3000, 5000, 10000, 45000]


def line_price(p, units):
    if p.get('kind') == 'per1000':
        return price_per_1000(p, units)
    return round(unit_price(p) * units, 2)


def cart_total(user_id):
    total = 0.0
    for pid, units in CART.get(user_id, {}).items():
        p = find_product(pid)
        if p:
            total += line_price(p, units)
    return round(total, 2)


def cart_count(user_id):
    return len(CART.get(user_id, {}))


# ---------------- Categories ----------------
def categories_kb(user_id, lang):
    rows = []
    for cat in CATALOG:
        rows.append([InlineKeyboardButton(text=cat['emoji'] + ' ' + tt(cat['title'], lang),
                                          callback_data='sc:' + cat['id'])])
    n = cart_count(user_id)
    cart_lbl = ('🧺 Корзина' if R(lang) else '🧺 Cart') + ((' (' + str(n) + ')') if n else '')
    rows.append([InlineKeyboardButton(text=cart_lbl, callback_data='scart')])
    return InlineKeyboardMarkup(inline_keyboard=rows)


async def show_categories(message, user_id, lang, edit=False):
    txt = ('📚 <b>Каталог</b>' + NL + 'Выберите категорию товаров:'
           if R(lang) else '📚 <b>Catalog</b>' + NL + 'Choose a category:')
    kb = categories_kb(user_id, lang)
    if edit:
        try:
            await message.edit_text(txt, reply_markup=kb)
            return
        except Exception:
            pass
    await message.answer(txt, reply_markup=kb)


# ---------------- Product list in a category ----------------
def products_kb(cat, lang):
    rows = []
    for p in cat.get('items', []):
        rows.append([InlineKeyboardButton(text=p['emoji'] + ' ' + tt(p['title'], lang),
                                          callback_data='sp:' + p['id'])])
    rows.append([InlineKeyboardButton(text=('⬅️ Категории' if R(lang) else '⬅️ Categories'),
                                      callback_data='sback')])
    return InlineKeyboardMarkup(inline_keyboard=rows)


# ---------------- Product detail with buy controls ----------------
async def product_kb(p, lang):
    rate = await get_usd_rub()
    rows = []
    if p.get('kind') == 'per1000':
        for amt in presets(p):
            price = line_price(p, amt)
            rows.append([InlineKeyboardButton(
                text=str(amt) + ' ' + p.get('unit', '') + ' — ' + money(price, 'RUB', rate),
                callback_data='sqa:' + p['id'] + ':' + str(amt))])
        rows.append([InlineKeyboardButton(
            text=('✏️ Своё количество' if R(lang) else '✏️ Custom amount'),
            callback_data='sqc:' + p['id'])])
    else:
        rows.append([InlineKeyboardButton(
            text=('➕ В корзину' if R(lang) else '➕ Add to cart'),
            callback_data='sadd:' + p['id'])])
    cat = _cat_of(p['id'])
    rows.append([
        InlineKeyboardButton(text=('🧺 Корзина' if R(lang) else '🧺 Cart'), callback_data='scart'),
        InlineKeyboardButton(text=('⬅️ Назад' if R(lang) else '⬅️ Back'),
                             callback_data='sc:' + (cat['id'] if cat else '')),
    ])
    return InlineKeyboardMarkup(inline_keyboard=rows)


async def product_text(p, lang):
    rate = await get_usd_rub()
    lines = ['🎀 <b>' + tt(p['title'], lang) + '</b>', '']
    if p.get('kind') == 'per1000':
        base_price = line_price(p, 1000)
        lines.append((('Цена за 1000 ' + p.get('unit', '') + ': ') if R(lang)
                      else ('Price per 1000 ' + p.get('unit', '') + ': ')) + both(base_price, rate))
        ml = min_line(p)
        if ml:
            lines.append((('Минимум: ') if R(lang) else 'Minimum: ') + both(ml, rate))
        if p.get('tier_units'):
            lines.append((('Скидка от ') if R(lang) else 'Discount from ') +
                          str(p['tier_units']) + ' ' + p.get('unit', ''))
        lines.append('')
        lines.append('Выберите количество:' if R(lang) else 'Choose amount:')
    else:
        price = unit_price(p)
        if p.get('face'):
            pct = discount_pct(p)
            official = money(float(p['face']), 'RUB', rate) + ' / $' + format(float(p['face']), '.0f')
            lines.append((('Цена: ') if R(lang) else 'Price: ') + both(price, rate) +
                         '  🔥 −' + str(pct) + '%')
            lines.append((('В официальном магазине: ') if R(lang) else 'Official store: ') +
                         '<s>' + official + '</s>')
        else:
            lines.append((('Цена: ') if R(lang) else 'Price: ') + both(price, rate))
    if p.get('note'):
        lines.append('')
        lines.append('ℹ️ ' + tt(p['note'], lang))
    return NL.join(lines)


# ---------------- Cart rendering ----------------
async def cart_view(user_id, lang):
    rate = await get_usd_rub()
    items = CART.get(user_id, {})
    if not items:
        txt = ('🧺 Корзина пуста.' + NL + 'Откройте 📚 Каталог и добавьте товары.'
               if R(lang) else '🧺 Cart is empty.' + NL + 'Open 📚 Catalog and add items.')
        kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(
            text=('📚 Каталог' if R(lang) else '📚 Catalog'), callback_data='sback')]])
        return txt, kb
    lines = ['🧺 <b>Корзина</b>' if R(lang) else '🧺 <b>Cart</b>', '']
    rows = []
    total = 0.0
    for pid, units in items.items():
        p = find_product(pid)
        if not p:
            continue
        price = line_price(p, units)
        total += price
        title = tt(p['title'], lang)
        if p.get('kind') == 'per1000':
            lines.append('• ' + title + ' — ' + str(units) + ' ' + p.get('unit', '') + ' = ' + money(price, 'RUB', rate))
        else:
            lines.append('• ' + title + ' ×' + str(units) + ' = ' + money(price, 'RUB', rate))
        rows.append([
            InlineKeyboardButton(text='−', callback_data='sdec:' + pid),
            InlineKeyboardButton(text=(title[:18]), callback_data='sp:' + pid),
            InlineKeyboardButton(text='＋', callback_data='sinc:' + pid),
            InlineKeyboardButton(text='🗑', callback_data='srm:' + pid),
        ])
    total = round(total, 2)
    lines.append('')
    lines.append(('<b>Итого:</b> ' if R(lang) else '<b>Total:</b> ') + both(total, rate))
    if total < MIN_ORDER_USD:
        lines.append((('⚠️ Минимальный заказ — $' + str(int(MIN_ORDER_USD)) +
                       ' (~' + str(int(MIN_ORDER_USD * rate)) + ' ₽)')
                      if R(lang) else
                      ('⚠️ Minimum order — $' + str(int(MIN_ORDER_USD)) +
                       ' (~' + str(int(MIN_ORDER_USD * rate)) + ' ₽)')))
    can = total >= MIN_ORDER_USD
    action = []
    if can:
        action.append(InlineKeyboardButton(
            text=('✅ Оформить · ' + money(total, 'RUB', rate)) if R(lang)
            else ('✅ Checkout · ' + money(total, 'RUB', rate)), callback_data='scheckout'))
    rows.append(action if action else [])
    rows.append([
        InlineKeyboardButton(text=('📚 Каталог' if R(lang) else '📚 Catalog'), callback_data='sback'),
        InlineKeyboardButton(text=('🗑 Очистить' if R(lang) else '🗑 Clear'), callback_data='sclear'),
    ])
    rows = [r for r in rows if r]
    return NL.join(lines), InlineKeyboardMarkup(inline_keyboard=rows)


# ---------------- Entry points (reply-keyboard text) ----------------
@shop_router.message(Command('shop', 'catalog'))
@shop_router.message(F.text.in_(CATALOG_LABELS))
async def open_catalog(message: Message):
    lang = await db.get_language(message.from_user.id)
    await show_categories(message, message.from_user.id, lang)


@shop_router.message(Command('cart'))
@shop_router.message(F.text.in_(CART_LABELS))
async def open_cart_msg(message: Message):
    lang = await db.get_language(message.from_user.id)
    txt, kb = await cart_view(message.from_user.id, lang)
    await message.answer(txt, reply_markup=kb)


# ---------------- Callbacks ----------------
@shop_router.callback_query(F.data == 'sback')
async def cb_back(cb: CallbackQuery):
    lang = await db.get_language(cb.from_user.id)
    await show_categories(cb.message, cb.from_user.id, lang, edit=True)
    await cb.answer()


@shop_router.callback_query(F.data.startswith('sc:'))
async def cb_category(cb: CallbackQuery):
    lang = await db.get_language(cb.from_user.id)
    cat_id = cb.data.split(':', 1)[1]
    cat = next((c for c in CATALOG if c['id'] == cat_id), None)
    if not cat:
        await cb.answer('?')
        return
    txt = cat['emoji'] + ' <b>' + tt(cat['title'], lang) + '</b>'
    try:
        await cb.message.edit_text(txt, reply_markup=products_kb(cat, lang))
    except Exception:
        await cb.message.answer(txt, reply_markup=products_kb(cat, lang))
    await cb.answer()


@shop_router.callback_query(F.data.startswith('sp:'))
async def cb_product(cb: CallbackQuery):
    lang = await db.get_language(cb.from_user.id)
    pid = cb.data.split(':', 1)[1]
    p = find_product(pid)
    if not p:
        await cb.answer('?')
        return
    txt = await product_text(p, lang)
    kb = await product_kb(p, lang)
    try:
        await cb.message.edit_text(txt, reply_markup=kb)
    except Exception:
        await cb.message.answer(txt, reply_markup=kb)
    await cb.answer()


@shop_router.callback_query(F.data.startswith('sadd:'))
async def cb_add_fixed(cb: CallbackQuery):
    lang = await db.get_language(cb.from_user.id)
    pid = cb.data.split(':', 1)[1]
    p = find_product(pid)
    if not p:
        await cb.answer('?')
        return
    cart = CART.setdefault(cb.from_user.id, {})
    cart[pid] = cart.get(pid, 0) + 1
    await cb.answer('➕ ' + (('Добавлено' if R(lang) else 'Added')))
    txt, kb = await cart_view(cb.from_user.id, lang)
    try:
        await cb.message.edit_text(txt, reply_markup=kb)
    except Exception:
        await cb.message.answer(txt, reply_markup=kb)


@shop_router.callback_query(F.data.startswith('sqa:'))
async def cb_add_per1000(cb: CallbackQuery):
    lang = await db.get_language(cb.from_user.id)
    _, pid, amt = cb.data.split(':')
    p = find_product(pid)
    if not p:
        await cb.answer('?')
        return
    units = int(amt)
    ml = min_line(p)
    if line_price(p, units) < ml:
        await cb.answer((('Минимум ' + money(ml, 'RUB', await get_usd_rub()))
                         if R(lang) else ('Minimum ' + money(ml, 'RUB', await get_usd_rub()))),
                        show_alert=True)
        return
    CART.setdefault(cb.from_user.id, {})[pid] = units
    await cb.answer('➕ ' + (('Добавлено' if R(lang) else 'Added')))
    txt, kb = await cart_view(cb.from_user.id, lang)
    try:
        await cb.message.edit_text(txt, reply_markup=kb)
    except Exception:
        await cb.message.answer(txt, reply_markup=kb)


@shop_router.callback_query(F.data.startswith('sqc:'))
async def cb_custom(cb: CallbackQuery):
    lang = await db.get_language(cb.from_user.id)
    pid = cb.data.split(':', 1)[1]
    p = find_product(pid)
    if not p:
        await cb.answer('?')
        return
    PENDING_QTY[cb.from_user.id] = pid
    unit = p.get('unit', '')
    await cb.message.answer(
        ('⌨️ Введите количество ' + unit + ' числом (напр. 3000):'
         if R(lang) else '⌨️ Enter amount of ' + unit + ' as a number (e.g. 3000):'))
    await cb.answer()


@shop_router.callback_query(F.data.startswith('sinc:'))
async def cb_inc(cb: CallbackQuery):
    await _adjust(cb, +1)


@shop_router.callback_query(F.data.startswith('sdec:'))
async def cb_dec(cb: CallbackQuery):
    await _adjust(cb, -1)


async def _adjust(cb, sign):
    lang = await db.get_language(cb.from_user.id)
    pid = cb.data.split(':', 1)[1]
    p = find_product(pid)
    cart = CART.get(cb.from_user.id, {})
    if not p or pid not in cart:
        await cb.answer()
        return
    if p.get('kind') == 'per1000':
        step = int(p.get('step', 1000))
        cart[pid] = max(0, cart[pid] + sign * step)
        if cart[pid] > 0 and line_price(p, cart[pid]) < min_line(p):
            cart[pid] = 0
    else:
        cart[pid] = max(0, cart[pid] + sign)
    if cart[pid] <= 0:
        cart.pop(pid, None)
    txt, kb = await cart_view(cb.from_user.id, lang)
    try:
        await cb.message.edit_text(txt, reply_markup=kb)
    except Exception:
        pass
    await cb.answer()


@shop_router.callback_query(F.data.startswith('srm:'))
async def cb_remove(cb: CallbackQuery):
    lang = await db.get_language(cb.from_user.id)
    pid = cb.data.split(':', 1)[1]
    CART.get(cb.from_user.id, {}).pop(pid, None)
    txt, kb = await cart_view(cb.from_user.id, lang)
    try:
        await cb.message.edit_text(txt, reply_markup=kb)
    except Exception:
        pass
    await cb.answer()


@shop_router.callback_query(F.data == 'sclear')
async def cb_clear(cb: CallbackQuery):
    lang = await db.get_language(cb.from_user.id)
    CART[cb.from_user.id] = {}
    txt, kb = await cart_view(cb.from_user.id, lang)
    try:
        await cb.message.edit_text(txt, reply_markup=kb)
    except Exception:
        pass
    await cb.answer()


@shop_router.callback_query(F.data == 'scart')
async def cb_cart(cb: CallbackQuery):
    lang = await db.get_language(cb.from_user.id)
    txt, kb = await cart_view(cb.from_user.id, lang)
    try:
        await cb.message.edit_text(txt, reply_markup=kb)
    except Exception:
        await cb.message.answer(txt, reply_markup=kb)
    await cb.answer()


@shop_router.callback_query(F.data == 'scheckout')
async def cb_checkout(cb: CallbackQuery):
    lang = await db.get_language(cb.from_user.id)
    items = CART.get(cb.from_user.id, {})
    if not items:
        await cb.answer()
        return
    rate = await get_usd_rub()
    u = cb.from_user
    contact = ('@' + u.username) if u.username else ('id' + str(u.id))
    raw = {
        'type': 'order', 'currency': 'RUB', 'rate': rate, 'lang': lang,
        'contact': contact,
        'items': [{'id': pid, 'qty': units} for pid, units in items.items()],
    }
    order_id = await send_order_from_raw(cb.message.bot, cb.message.chat.id, u.id, raw, lang)
    if order_id:
        CART[cb.from_user.id] = {}
        try:
            await cb.message.edit_reply_markup(reply_markup=None)
        except Exception:
            pass
    await cb.answer()


# ---------------- Custom amount typed by the user ----------------
# Only fires while the user is actually being asked for a quantity; otherwise
# a plain number falls through to the support catch-all.
@shop_router.message(
    F.text.func(lambda t: t is not None and t.strip().replace(' ', '').isdigit()),
    lambda m: m.from_user is not None and m.from_user.id in PENDING_QTY,
)
async def on_custom_amount(message: Message):
    user_id = message.from_user.id
    pid = PENDING_QTY.get(user_id)
    if not pid:
        return
    lang = await db.get_language(user_id)
    p = find_product(pid)
    if not p:
        PENDING_QTY.pop(user_id, None)
        return
    units = int(message.text.strip().replace(' ', ''))
    if units <= 0:
        await message.answer('⚠️ ' + ('Введите число больше 0.' if R(lang) else 'Enter a number > 0.'))
        return
    ml = min_line(p)
    if line_price(p, units) < ml:
        await message.answer('⚠️ ' + (('Минимум: ' + money(ml, 'RUB', await get_usd_rub()))
                                        if R(lang) else ('Minimum: ' + money(ml, 'RUB', await get_usd_rub()))))
        return
    CART.setdefault(user_id, {})[pid] = units
    PENDING_QTY.pop(user_id, None)
    txt, kb = await cart_view(user_id, lang)
    await message.answer(txt, reply_markup=kb)
