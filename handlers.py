"""Customer handlers for Oncedshop bot: start, language, payments, my orders."""
import logging
from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery, LabeledPrice, PreCheckoutQuery
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import WEBAPP_URL, MIN_ORDER_USD, CRYPTO_WALLETS, CRYPTOBOT_URL
from utils import usd_to_stars, crypto_amount, format_money, get_usd_rub
from common import NL, esc, user_label
import database as db
from keyboards import lang_kb, main_reply_kb, payment_kb, crypto_kb, ORDERS_LABELS
from orders import PENDING
from support import notify_staff

router = Router(name='customer')
log = logging.getLogger(__name__)

STATUS_RU = {'created': 'ожидает оплаты', 'await_support': 'оплата у поддержки',
             'paid': 'оплачен', 'done': 'выдан', 'cancelled': 'отменён'}
STATUS_EN = {'created': 'awaiting payment', 'await_support': 'pay via support',
             'paid': 'paid', 'done': 'delivered', 'cancelled': 'cancelled'}


def R(lang): return lang == 'ru'
def money(usd, currency='USD', rate=None): return format_money(usd, currency, rate)


async def notify_paid(bot, order_id, buyer=None, method=''):
    try: o = await db.get_order(order_id)
    except Exception: o = None
    title  = (o.get('title')      if o else '') or ''
    amount = (o.get('amount_usd') if o else 0)  or 0
    uid    = (o.get('user_id')    if o else None)
    who    = buyer or (('id' + str(uid)) if uid else '—')
    lines = [
        '💰 <b>Новая оплата</b>',
        'Заказ: <code>' + esc(order_id) + '</code>',
        'Товар: ' + esc(title),
        'Сумма: ' + money(amount, 'USD') + '  ·  ' + money(amount, 'RUB'),
        'Клиент: ' + esc(who) + ((' · id<code>' + str(uid) + '</code>') if uid else ''),
    ]
    if method: lines.append('Оплата: ' + esc(method))
    lines.append('')
    lines.append('Выдайте товар и нажмите «📦 Выдан» — клиент получит уведомление.')
    await notify_staff(bot, NL.join(lines), user_id=uid, order_id=order_id)


# ─ Start & language ─────────────────────────────────────────────────────────────
@router.message(CommandStart())
async def cmd_start(message: Message):
    '''Always acknowledge /start even if the persistent DB is temporarily unavailable.'''
    u = message.from_user
    # Answer first: a locked/read-only Railway volume must never make the bot look dead.
    await message.answer(
        '◼️ <b>Oncedshop</b>' + NL + 'Выберите язык / Choose language:',
        reply_markup=lang_kb(),
    )
    try:
        await db.upsert_user(u.id, u.username or '', u.full_name or '')
    except Exception as e:
        log.exception('start: failed to save user %s: %s', u.id, e)


@router.message(Command('id'))
async def cmd_id(message: Message):
    u = message.from_user
    await message.answer(
        '🆔 Ваш Telegram ID: <code>' + str(u.id) + '</code>' + NL +
        'Username: @' + esc(u.username or '—') + NL +
        'Chat ID: <code>' + str(message.chat.id) + '</code>',
    )


@router.callback_query(F.data.startswith('lang:'))
async def on_lang(cb: CallbackQuery):
    lang = cb.data.split(':')[1]
    await db.set_language(cb.from_user.id, lang)
    try: await cb.message.delete()
    except Exception: pass
    await send_menu(cb.message, lang)
    await cb.answer()


async def send_menu(message: Message, lang):
    rate = await get_usd_rub()
    if R(lang):
        text = (
            '◼️ <b>Oncedshop</b> — цифровой магазин' + NL + NL +
            'Откройте <b>🛒 Магазин</b> или <b>📎 Каталог</b>, выберите товары и оформите заказ.' + NL +
            'Оплата: Telegram Stars, крипта, CryptoBot, баланс.' + NL +
            'Мин. заказ — $' + str(int(MIN_ORDER_USD)) + ' (~' + str(int(MIN_ORDER_USD * rate)) + ' ₽).' + NL +
            'Курс: 1$ ≈ ' + format(rate, '.2f') + ' ₽' + NL + NL +
            '💬 Вопрос? Просто напишите сюда — ответит оператор.'
        )
    else:
        text = (
            '◼️ <b>Oncedshop</b> — digital store' + NL + NL +
            'Open <b>🛒 Shop</b> or <b>📎 Catalog</b>, pick items and place your order.' + NL +
            'Pay with Telegram Stars, crypto, CryptoBot or balance.' + NL +
            'Minimum order — $' + str(int(MIN_ORDER_USD)) + ' (~' + str(int(MIN_ORDER_USD * rate)) + ' ₽).' + NL +
            'Rate: 1$ ≈ ' + format(rate, '.2f') + ' ₽' + NL + NL +
            '💬 Questions? Just type here — an operator will answer.'
        )
    await message.answer(text, reply_markup=main_reply_kb(lang))
    if not WEBAPP_URL:
        log.warning('WEBAPP_URL is not set — mini-app button hidden')


@router.message(F.contact)
async def on_contact(message: Message):
    phone = message.contact.phone_number
    await db.save_phone(message.from_user.id, phone)
    lang = await db.get_language(message.from_user.id)
    await message.answer('✅ Контакт сохранён.' if R(lang) else '✅ Contact saved.', reply_markup=main_reply_kb(lang))


@router.message(F.web_app_data)
async def on_webapp(message: Message):
    from orders import send_order_from_raw
    lang = await db.get_language(message.from_user.id)
    try:
        await send_order_from_raw(message.bot, message.chat.id, message.from_user.id,
                                  message.web_app_data.data, lang)
    except Exception as e:
        log.exception('web_app_data: %s', e)
        await message.answer('⚠️ Ошибка при обработке заказа. Напишите нам сюда, поможем.' if R(lang)
                             else '⚠️ Order processing error. Write to us here, we will help.',
                             reply_markup=main_reply_kb(lang))


# ─ Telegram Stars ─────────────────────────────────────────────────────────────
@router.callback_query(F.data.startswith('pay:stars:'))
async def pay_stars(cb: CallbackQuery):
    order_id = cb.data.split(':')[2]
    info = PENDING.get(order_id)
    lang = info['lang'] if info else await db.get_language(cb.from_user.id)
    if not info: await cb.answer('⏳ Заказ устарел, оформите заново' if R(lang) else '⏳ Order expired, please reorder', show_alert=True); return
    rate = info.get('rate') or await get_usd_rub()
    stars = usd_to_stars(info['total'], rate)
    title = ('Заказ ' if R(lang) else 'Order ') + order_id
    desc  = ('Оплата ' if R(lang) else 'Payment ') + money(info['total'], 'USD', rate)
    await db.set_order_payment(order_id, 'stars', str(stars) + ' XTR')
    try:
        await cb.message.answer_invoice(
            title=title, description=desc, payload='order:' + order_id,
            currency='XTR', prices=[LabeledPrice(label=title, amount=stars)],
            provider_token='',
        )
    except Exception as e:
        log.exception('invoice: %s', e)
        await cb.message.answer('⚠️ Не удалось создать счёт. Напишите нам сюда.' if R(lang)
                                else '⚠️ Could not create invoice. Write to us here.')
    await cb.answer()


@router.callback_query(F.data.startswith('pay:balance:'))
async def pay_balance(cb: CallbackQuery):
    order_id = cb.data.split(':')[2]
    info = PENDING.get(order_id)
    lang = info['lang'] if info else await db.get_language(cb.from_user.id)
    if not info: await cb.answer('⏳'); return
    rate = info.get('rate') or await get_usd_rub()
    total = info['total']
    bal = await db.get_balance(cb.from_user.id)
    if bal + 1e-9 < total:
        need = round(total - bal, 2)
        txt = (('⚠️ Недостаточно средств.' + NL + 'Баланс: ' + money(bal, 'USD', rate) + NL + 'Нужно: ' + money(need, 'USD', rate) +
                NL + NL + 'Пополнить баланс можно через поддержку — просто напишите сюда.') if R(lang) else
               ('⚠️ Insufficient funds.' + NL + 'Balance: ' + money(bal, 'USD', rate) + NL + 'Need: ' + money(need, 'USD', rate) +
                NL + NL + 'Top up via support — just write here.'))
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='⬅️ Назад' if R(lang) else '⬅️ Back', callback_data='pay:back:' + order_id)],
        ])
        try: await cb.message.edit_text(txt, reply_markup=kb)
        except Exception: pass
        await cb.answer(); return
    remain = round(bal - total, 2)
    await db.set_balance(cb.from_user.id, remain)
    await db.set_order_payment(order_id, 'balance', money(total, 'USD', rate))
    await db.set_order_status(order_id, 'paid')
    txt = (('✅ Оплачено с баланса!' + NL + 'Заказ: <code>' + order_id + '</code>' + NL + 'Остаток: ' + money(remain, 'USD', rate)) if R(lang) else
           ('✅ Paid from balance!' + NL + 'Order: <code>' + order_id + '</code>' + NL + 'Remaining: ' + money(remain, 'USD', rate)))
    try: await cb.message.edit_text(txt)
    except Exception: pass
    uname = user_label(cb.from_user.id, cb.from_user.username, cb.from_user.full_name)
    await notify_paid(cb.bot, order_id, uname, 'balance')
    await cb.answer('✅')


@router.pre_checkout_query()
async def pre_checkout(q: PreCheckoutQuery): await q.answer(ok=True)


@router.message(F.successful_payment)
async def on_paid(message: Message):
    lang = await db.get_language(message.from_user.id)
    payload  = message.successful_payment.invoice_payload
    order_id = payload.split(':')[1] if ':' in payload else payload
    await db.set_order_status(order_id, 'paid')
    uname = user_label(message.from_user.id, message.from_user.username, message.from_user.full_name)
    await notify_paid(message.bot, order_id, uname, 'Telegram Stars')
    txt = (('✅ Оплата получена! Заказ <code>' + order_id + '</code> передан в обработку.' + NL +
            'Оператор выдаст товар в этом чате.') if R(lang) else
           ('✅ Payment received! Order <code>' + order_id + '</code> is being processed.' + NL +
            'The operator will deliver in this chat.'))
    await message.answer(txt, reply_markup=main_reply_kb(lang))


@router.callback_query(F.data.startswith('pay:crypto:'))
async def pay_crypto(cb: CallbackQuery):
    order_id = cb.data.split(':')[2]
    info = PENDING.get(order_id)
    lang = info['lang'] if info else await db.get_language(cb.from_user.id)
    if not info: await cb.answer('⏳'); return
    await cb.message.edit_text('Выберите монету:' if R(lang) else 'Choose a coin:', reply_markup=crypto_kb(order_id, lang))
    await cb.answer()


@router.callback_query(F.data.startswith('coin:'))
async def show_coin(cb: CallbackQuery):
    _, code, order_id = cb.data.split(':')
    info = PENDING.get(order_id)
    lang = info['lang'] if info else await db.get_language(cb.from_user.id)
    if not info: await cb.answer('⏳'); return
    w = CRYPTO_WALLETS.get(code)
    if not w: await cb.answer('?'); return
    rate   = info.get('rate') or await get_usd_rub()
    amount = crypto_amount(info['total'], w['usd'], w['dp'])
    await db.set_order_payment(order_id, code, str(amount) + ' ' + w['label'])
    txt = (w['emoji'] + ' <b>' + w['label'] + '</b>' + NL + NL +
           ('Сумма: <b>' if R(lang) else 'Amount: <b>') + str(amount) + '</b>' + NL +
           '(≈ ' + money(info['total'], 'USD', rate) + ')' + NL + NL +
           ('Адрес:' if R(lang) else 'Address:') + NL + '<code>' + w['address'] + '</code>' + NL + NL +
           (('После оплаты пришлите сюда скриншот/хеш транзакции и номер заказа <code>' + order_id + '</code>.') if R(lang)
            else ('After paying, send the screenshot/tx hash and order number <code>' + order_id + '</code> right here.')))
    await cb.message.edit_text(txt, reply_markup=crypto_kb(order_id, lang))
    await cb.answer()


@router.callback_query(F.data.startswith('pay:cbot:'))
async def pay_cbot(cb: CallbackQuery):
    order_id = cb.data.split(':')[2]
    info = PENDING.get(order_id)
    lang = info['lang'] if info else await db.get_language(cb.from_user.id)
    rate  = (info.get('rate') if info else None) or await get_usd_rub()
    total = info['total'] if info else 0
    link = await db.get_setting('cryptobot_link', CRYPTOBOT_URL) or CRYPTOBOT_URL
    await db.set_order_payment(order_id, 'cbot', link)
    txt = ('🤖 <b>CryptoBot</b>' + NL + NL +
           ('Сумма: ' if R(lang) else 'Amount: ') + money(total, 'USD', rate) + NL +
           (('Нажмите кнопку ниже — вы перейдёте в CryptoBot и оплатите счёт там. После оплаты напишите сюда номер заказа <code>' + order_id + '</code>.') if R(lang)
            else ('Tap the button below — you will be redirected to CryptoBot to pay. After paying, send the order number <code>' + order_id + '</code> here.')))
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='🤖 Оплатить в CryptoBot' if R(lang) else '🤖 Pay in CryptoBot', url=link)],
        [InlineKeyboardButton(text='⬅️ Назад' if R(lang) else '⬅️ Back', callback_data='pay:back:' + order_id)],
    ])
    await cb.message.edit_text(txt, reply_markup=kb); await cb.answer()


@router.callback_query(F.data.startswith('pay:back:'))
async def pay_back(cb: CallbackQuery):
    order_id = cb.data.split(':')[2]
    info = PENDING.get(order_id)
    lang = info['lang'] if info else await db.get_language(cb.from_user.id)
    rate  = (info.get('rate') if info else None) or await get_usd_rub()
    total = info['total'] if info else 0
    txt = (('🧾 Заказ <code>' + order_id + '</code>' + NL + 'Итого: ' + money(total, 'USD', rate) + NL + NL + 'Выберите способ оплаты:') if R(lang) else
           ('🧾 Order <code>' + order_id + '</code>' + NL + 'Total: ' + money(total, 'USD', rate) + NL + NL + 'Choose a payment method:'))
    await cb.message.edit_text(txt, reply_markup=payment_kb(order_id, lang))
    await cb.answer()


@router.callback_query(F.data.startswith('pay:support:'))
async def pay_support(cb: CallbackQuery):
    order_id = cb.data.split(':')[2]
    info = PENDING.get(order_id)
    lang = info['lang'] if info else await db.get_language(cb.from_user.id)
    rate  = (info.get('rate') if info else None) or await get_usd_rub()
    total = info['total'] if info else 0
    await db.set_order_payment(order_id, 'support', 'manual')
    await db.set_order_status(order_id, 'await_support')
    u = cb.from_user
    uname = user_label(u.id, u.username, u.full_name)
    txt = (('👤 <b>Оплата через поддержку</b>' + NL + NL +
            'Заказ: <code>' + order_id + '</code>' + NL +
            'Сумма: ' + money(total, 'USD', rate) + NL + NL +
            'Оператор уже уведомлён и напишет вам сюда. Можете сразу написать, как удобнее оплатить.') if R(lang) else
           ('👤 <b>Pay via support</b>' + NL + NL +
            'Order: <code>' + order_id + '</code>' + NL +
            'Amount: ' + money(total, 'USD', rate) + NL + NL +
            'The operator has been notified and will write to you here. You may describe your preferred payment method right away.'))
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='⬅️ Назад' if R(lang) else '⬅️ Back', callback_data='pay:back:' + order_id)],
    ])
    await cb.message.edit_text(txt, reply_markup=kb)
    note = ('🔔 <b>Клиент выбрал оплату через поддержку</b>' + NL +
            'Заказ: <code>' + order_id + '</code> — ' + money(total, 'USD', rate) + ' · ' + money(total, 'RUB', rate) + NL +
            'Клиент: ' + esc(uname) + ' · id<code>' + str(u.id) + '</code>' + NL + NL +
            'Нажмите «✉️ Ответить», чтобы договориться об оплате.')
    await db.ticket_touch(u.id, 'in', 'Оплата через поддержку: ' + order_id)
    await notify_staff(cb.bot, note, user_id=u.id, order_id=order_id)
    await cb.answer()


# ─ My orders ────────────────────────────────────────────────────────────────────
async def my_orders_text(user_id, lang):
    rows = await db.get_user_orders(user_id)
    if not rows:
        return 'Заказов пока нет.' if R(lang) else 'No orders yet.'
    labels = STATUS_RU if R(lang) else STATUS_EN
    out = ['🧾 <b>Ваши заказы</b>' if R(lang) else '🧾 <b>Your orders</b>', '']
    for oid, title, qty, amount, status, created in rows:
        out.append('<code>' + esc(oid) + '</code> — ' + esc(title or '') + ' — ' + money(amount or 0, 'USD') +
                   ' · ' + labels.get(status, esc(status or '')))
    return NL.join(out)


@router.message(Command('orders'))
@router.message(F.text.in_(ORDERS_LABELS))
async def my_orders(message: Message):
    lang = await db.get_language(message.from_user.id)
    await message.answer(await my_orders_text(message.from_user.id, lang))
