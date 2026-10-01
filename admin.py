"""Admin panel for Oncedshop: /admin menu, orders, users, balance, leads."""
import logging

from aiogram import Router, F
from aiogram.filters import Command, CommandObject
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from config import MONITOR_CHATS, CRYPTOBOT_URL
from common import NL, esc, user_label, IsAdmin
import database as db
from keyboards import main_reply_kb

admin_router = Router(name='admin')
admin_router.message.filter(IsAdmin())
admin_router.callback_query.filter(IsAdmin())

log = logging.getLogger(__name__)
LEADS_PER_PAGE = 5
ORDERS_PER_PAGE = 6
USERS_PER_PAGE = 8

_STATUS_LABEL = {'new': '🔄 Новый', 'done': '✅ Обработан'}
ORDER_STATUS = {
    'created': '🕐 Ожидает оплаты',
    'await_support': '👤 Оплата у поддержки',
    'paid': '💰 Оплачен',
    'done': '✅ Выдан',
    'cancelled': '❌ Отменён',
}


def R(lang):
    return lang == 'ru'


def _short(text, n=180):
    text = esc(text).replace(NL, ' ')
    return text if len(text) <= n else text[:n] + '…'


def _money(v):
    return '$' + format(float(v or 0), '.2f')


def _ts(s):
    return (s or '')[5:16].replace('T', ' ')


# ─────────────────────────── menu / stats ─────────────────────────────────────
def menu_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='📨 Обращения', callback_data='sup:list:0'),
         InlineKeyboardButton(text='🧾 Заказы', callback_data='adm:orders:0:all')],
        [InlineKeyboardButton(text='👥 Пользователи', callback_data='adm:users:0'),
         InlineKeyboardButton(text='🎯 Лиды', callback_data='leadpg:0')],
        [InlineKeyboardButton(text='🔄 Обновить', callback_data='adm:menu')],
    ])


async def render_menu():
    s = await db.stats()
    out = [
        '◼️ <b>Oncedshop — Админ панель</b>', '',
        '📨 Обращений открыто: <b>' + str(s['tickets_open']) + '</b>' +
        ('  · непрочитанных: <b>' + str(s['tickets_unread']) + '</b>' if s['tickets_unread'] else ''),
        '🧾 Заказов: <b>' + str(s['orders']) + '</b>  · оплачено: ' + str(s['orders_paid']) +
        '  · ждут: ' + str(s['orders_pending']),
        '💵 Выручка (оплаченные): <b>' + _money(s['revenue']) + '</b>',
        '👥 Пользователей: <b>' + str(s['users']) + '</b>',
        '🎯 Новых лидов: ' + str(s['leads_new']),
        '',
        '<b>Команды</b>',
        '/tickets — обращения · /orders — заказы · /users — пользователи',
        '/reply <code>id</code> — написать клиенту · /stop — выйти из режима ответа',
        '/done <code>ORDER</code> — отметить заказ выданным',
        '/balance <code>id</code> <code>±сумма</code> — изменить баланс ($)',
        '/discount <code>id</code> <code>%</code> — персональная скидка',
        '/history <code>id</code> — история переписки · /close <code>id</code> — закрыть обращение',
        '/score <code>ссылка</code> — задать счёт CryptoBot (без аргумента — показать текущий)',
    ]
    return NL.join(out), menu_kb()


@admin_router.message(Command('admin'))
async def cmd_admin(message: Message):
    text, kb = await render_menu()
    await message.answer(text, reply_markup=kb, disable_web_page_preview=True)


@admin_router.callback_query(F.data == 'adm:menu')
async def cb_menu(cb: CallbackQuery):
    text, kb = await render_menu()
    try:
        await cb.message.edit_text(text, reply_markup=kb, disable_web_page_preview=True)
    except Exception:
        await cb.message.answer(text, reply_markup=kb, disable_web_page_preview=True)
    await cb.answer()


# ─────────────────────────── CryptoBot invoice link (/score) ──────────────────
@admin_router.message(Command('score'))
async def cmd_score(message: Message, command: CommandObject):
    link = (command.args or '').strip()
    if not link:
        current = await db.get_setting('cryptobot_link', CRYPTOBOT_URL) or CRYPTOBOT_URL
        await message.answer(
            '🤖 <b>Текущий счёт CryptoBot:</b>' + NL + current + NL + NL +
            'Чтобы изменить: <code>/score ссылка</code>',
            disable_web_page_preview=True,
        )
        return
    if not (link.startswith('http://') or link.startswith('https://') or link.startswith('t.me/')):
        await message.answer('⚠️ Похоже, это не ссылка. Пример: <code>/score t.me/send?start=XXXX</code>')
        return
    if link.startswith('t.me/'):
        link = 'https://' + link
    await db.set_setting('cryptobot_link', link)
    await message.answer('✅ Счёт CryptoBot обновлён:' + NL + esc(link), disable_web_page_preview=True)


# ─────────────────────────── orders ───────────────────────────────────────────
def _order_buttons(oid, uid, status):
    btns = []
    if status not in ('done', 'cancelled'):
        btns.append(InlineKeyboardButton(text='✅ Выдан', callback_data='adm:odone:' + oid + ':' + str(uid)))
    btns.append(InlineKeyboardButton(text='✉️ Клиенту', callback_data='sup:reply:' + str(uid)))
    if status not in ('done', 'cancelled'):
        btns.append(InlineKeyboardButton(text='❌', callback_data='adm:ocancel:' + oid + ':' + str(uid)))
    return btns


async def render_orders(page=0, flt='all'):
    status = None if flt == 'all' else flt
    total = await db.count_orders(status)
    pages = max(1, (total + ORDERS_PER_PAGE - 1) // ORDERS_PER_PAGE)
    page = max(0, min(page, pages - 1))
    rows = await db.get_all_orders(ORDERS_PER_PAGE, page * ORDERS_PER_PAGE, status)
    title = {'all': 'все', 'paid': 'оплаченные', 'await_support': 'через поддержку', 'created': 'ожидают'}.get(flt, flt)
    out = ['🧾 <b>Заказы</b> · ' + title + ' · ' + str(total), '']
    kb_rows = []
    if not rows:
        out.append('Заказов нет.')
    for oid, uid, otitle, qty, amount, st, pay, created in rows:
        u = await db.get_user(uid) if uid else None
        label = user_label(uid, u.get('username') if u else None, u.get('full_name') if u else None)
        out.append('<code>' + esc(oid) + '</code> ' + ORDER_STATUS.get(st, esc(st or '')))
        out.append('   ' + _short(otitle, 70))
        out.append('   ' + _money(amount) + ' · ' + esc(pay or '—') + ' · ' + esc(label) +
                   ' id<code>' + str(uid) + '</code> · ' + _ts(created))
        out.append('')
        kb_rows.append([InlineKeyboardButton(text='· ' + oid + ' ·', callback_data='adm:onoop')] )
        kb_rows.append(_order_buttons(oid, uid, st))
    filt = [
        InlineKeyboardButton(text=('• ' if flt == 'all' else '') + 'Все', callback_data='adm:orders:0:all'),
        InlineKeyboardButton(text=('• ' if flt == 'paid' else '') + 'Оплачены', callback_data='adm:orders:0:paid'),
        InlineKeyboardButton(text=('• ' if flt == 'await_support' else '') + 'Поддержка', callback_data='adm:orders:0:await_support'),
    ]
    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton(text='⬅️', callback_data='adm:orders:' + str(page - 1) + ':' + flt))
    nav.append(InlineKeyboardButton(text=str(page + 1) + '/' + str(pages), callback_data='adm:orders:' + str(page) + ':' + flt))
    if page < pages - 1:
        nav.append(InlineKeyboardButton(text='➡️', callback_data='adm:orders:' + str(page + 1) + ':' + flt))
    kb_rows.append(filt)
    kb_rows.append(nav)
    kb_rows.append([InlineKeyboardButton(text='⬅️ Админ-меню', callback_data='adm:menu')])
    return NL.join(out), InlineKeyboardMarkup(inline_keyboard=kb_rows)


async def render_user_orders(uid, limit=8):
    rows = await db.get_user_orders(uid, limit)
    u = await db.get_user(uid)
    label = user_label(uid, u.get('username') if u else None, u.get('full_name') if u else None)
    out = ['🧾 <b>Заказы ' + esc(label) + '</b> (id<code>' + str(uid) + '</code>)']
    if u:
        out.append('Баланс: ' + _money(u.get('balance')) + ' · Скидка: ' + str(int(float(u.get('discount') or 0))) + '%')
    out.append('')
    kb_rows = []
    if not rows:
        out.append('Заказов нет.')
    for oid, title, qty, amount, st, created in rows:
        out.append('<code>' + esc(oid) + '</code> ' + ORDER_STATUS.get(st, esc(st or '')) + ' · ' + _money(amount))
        out.append('   ' + _short(title, 70) + ' · ' + _ts(created))
        if st not in ('done', 'cancelled'):
            kb_rows.append([InlineKeyboardButton(text='✅ Выдан ' + oid, callback_data='adm:odone:' + oid + ':' + str(uid))])
    kb_rows.append([InlineKeyboardButton(text='✉️ Написать', callback_data='sup:reply:' + str(uid)),
                    InlineKeyboardButton(text='🕘 История', callback_data='sup:hist:' + str(uid))])
    return NL.join(out), InlineKeyboardMarkup(inline_keyboard=kb_rows)


@admin_router.message(Command('orders'))
async def cmd_orders(message: Message):
    text, kb = await render_orders(0, 'all')
    await message.answer(text, reply_markup=kb)


@admin_router.callback_query(F.data.startswith('adm:orders:'))
async def cb_orders(cb: CallbackQuery):
    _, _, page, flt = cb.data.split(':', 3)
    text, kb = await render_orders(int(page), flt)
    try:
        await cb.message.edit_text(text, reply_markup=kb)
    except Exception:
        pass
    await cb.answer()


@admin_router.callback_query(F.data == 'adm:onoop')
async def cb_onoop(cb: CallbackQuery):
    await cb.answer()


async def _mark_done(bot, order_id, uid=None):
    o = await db.get_order(order_id)
    if not o:
        return False, 'Заказ не найден.'
    await db.set_order_status(order_id, 'done')
    uid = uid or o.get('user_id')
    if uid:
        lang = await db.get_language(uid)
        try:
            await bot.send_message(
                uid,
                ('✅ Заказ <code>' + order_id + '</code> выдан!' + NL + esc(o.get('title') or '') + NL + NL +
                 'Спасибо за покупку ❤️ Если что-то не так — напишите сюда.') if R(lang) else
                ('✅ Order <code>' + order_id + '</code> delivered!' + NL + esc(o.get('title') or '') + NL + NL +
                 'Thank you ❤️ If anything is wrong — just write here.'),
                reply_markup=main_reply_kb(lang),
            )
        except Exception as e:
            return True, 'Статус обновлён, но клиенту не доставлено: ' + esc(e)
    return True, 'Заказ ' + order_id + ' отмечен выданным, клиент уведомлён.'


@admin_router.callback_query(F.data.startswith('adm:odone:'))
async def cb_order_done(cb: CallbackQuery):
    parts = cb.data.split(':')
    oid = parts[2]
    uid = int(parts[3]) if len(parts) > 3 and parts[3].isdigit() else None
    ok, msg = await _mark_done(cb.bot, oid, uid)
    await cb.answer(msg[:190], show_alert=not ok)
    if ok:
        try:
            await cb.message.reply('✅ <code>' + oid + '</code> — выдан.')
        except Exception:
            pass


@admin_router.callback_query(F.data.startswith('adm:ocancel:'))
async def cb_order_cancel(cb: CallbackQuery):
    parts = cb.data.split(':')
    oid = parts[2]
    await db.set_order_status(oid, 'cancelled')
    await cb.answer('❌ ' + oid + ' отменён')
    try:
        await cb.message.reply('❌ <code>' + oid + '</code> — отменён.')
    except Exception:
        pass


@admin_router.message(Command('done'))
async def cmd_done(message: Message, command: CommandObject):
    oid = (command.args or '').strip().upper()
    if not oid:
        await message.answer('Использование: <code>/done ONC-XXXXXXXX</code>')
        return
    ok, msg = await _mark_done(message.bot, oid)
    await message.answer(('✅ ' if ok else '⚠️ ') + msg)


# ─────────────────────────── users / balance / discount ───────────────────────
async def render_users(page=0):
    total = await db.count_users()
    pages = max(1, (total + USERS_PER_PAGE - 1) // USERS_PER_PAGE)
    page = max(0, min(page, pages - 1))
    rows = await db.get_all_users(USERS_PER_PAGE, page * USERS_PER_PAGE)
    out = ['👥 <b>Пользователи</b> · ' + str(total), '']
    kb_rows = []
    for uid, uname, name, bal, disc, created in rows:
        label = user_label(uid, uname, name)
        out.append('<b>' + esc(label) + '</b> id<code>' + str(uid) + '</code>')
        out.append('   Бал: ' + _money(bal) + ' · Ск: ' + str(int(float(disc or 0))) + '% · ' + _ts(created))
        kb_rows.append([
            InlineKeyboardButton(text='✉️ ' + label[:16], callback_data='sup:reply:' + str(uid)),
            InlineKeyboardButton(text='🧾', callback_data='sup:orders:' + str(uid)),
            InlineKeyboardButton(text='🕘', callback_data='sup:hist:' + str(uid)),
        ])
    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton(text='⬅️', callback_data='adm:users:' + str(page - 1)))
    nav.append(InlineKeyboardButton(text=str(page + 1) + '/' + str(pages), callback_data='adm:users:' + str(page)))
    if page < pages - 1:
        nav.append(InlineKeyboardButton(text='➡️', callback_data='adm:users:' + str(page + 1)))
    kb_rows.append(nav)
    kb_rows.append([InlineKeyboardButton(text='⬅️ Админ-меню', callback_data='adm:menu')])
    return NL.join(out), InlineKeyboardMarkup(inline_keyboard=kb_rows)


@admin_router.message(Command('users'))
async def cmd_users(message: Message):
    text, kb = await render_users(0)
    await message.answer(text, reply_markup=kb)


@admin_router.callback_query(F.data.startswith('adm:users:'))
async def cb_users(cb: CallbackQuery):
    page = int(cb.data.split(':')[2])
    text, kb = await render_users(page)
    try:
        await cb.message.edit_text(text, reply_markup=kb)
    except Exception:
        pass
    await cb.answer()


async def _resolve(query):
    q = (query or '').strip()
    if q.lstrip('-').isdigit():
        return int(q)
    u = await db.find_user(q)
    return int(u['user_id']) if u else None


@admin_router.message(Command('balance'))
async def cmd_balance(message: Message, command: CommandObject):
    args = (command.args or '').split()
    if len(args) < 1:
        await message.answer('Использование: <code>/balance id</code> — показать, '
                             '<code>/balance id +10</code> / <code>-5</code> / <code>=20</code> — изменить.')
        return
    uid = await _resolve(args[0])
    if not uid:
        await message.answer('Пользователь не найден.')
        return
    if len(args) == 1:
        await message.answer('Баланс id' + str(uid) + ': ' + _money(await db.get_balance(uid)))
        return
    raw = args[1].replace(',', '.')
    try:
        if raw.startswith('='):
            await db.set_balance(uid, float(raw[1:]))
            new = float(raw[1:])
        else:
            new = await db.add_balance(uid, float(raw))
    except ValueError:
        await message.answer('Сумма должна быть числом, например +10 или -5.5')
        return
    await message.answer('✅ Баланс id' + str(uid) + ' теперь ' + _money(new))
    lang = await db.get_language(uid)
    try:
        await message.bot.send_message(
            uid, ('💰 Ваш баланс обновлён: ' if R(lang) else '💰 Your balance was updated: ') + _money(new))
    except Exception:
        pass


@admin_router.message(Command('discount'))
async def cmd_discount(message: Message, command: CommandObject):
    args = (command.args or '').split()
    if len(args) < 2:
        await message.answer('Использование: <code>/discount id 10</code> (процент, 0 — убрать)')
        return
    uid = await _resolve(args[0])
    if not uid:
        await message.answer('Пользователь не найден.')
        return
    try:
        pct = max(0.0, min(100.0, float(args[1].replace('%', '').replace(',', '.'))))
    except ValueError:
        await message.answer('Процент должен быть числом.')
        return
    await db.set_discount(uid, pct)
    await message.answer('✅ Скидка id' + str(uid) + ': ' + format(pct, '.0f') + '%')


# ─────────────────────────── leads (chat monitor) ─────────────────────────────
async def render_leads(page=0):
    total = await db.count_leads()
    new_cnt = await db.count_leads('new')
    pages = max(1, (total + LEADS_PER_PAGE - 1) // LEADS_PER_PAGE)
    page = max(0, min(page, pages - 1))
    rows = await db.get_leads(LEADS_PER_PAGE, page * LEADS_PER_PAGE)
    out = ['🎯 <b>Лиды из чатов</b>',
           'Чат: ' + (', '.join('@' + c for c in MONITOR_CHATS) if MONITOR_CHATS else '—'),
           'Всего: ' + str(total) + '  ·  Новых: ' + str(new_cnt), '']
    if not rows:
        out.append('Лидов пока нет.')
    kb_rows = []
    for r in rows:
        (lid, source, chat, mid, author, author_id, text, matched, triggers, link, status, created) = r
        head = '#' + str(lid) + ' ' + _STATUS_LABEL.get(status, status)
        who = ('@' + author) if author else ('id' + str(author_id or ''))
        out.append('<b>' + head + '</b> — ' + esc(who))
        out.append('🔑 ' + esc(triggers or '') + '  ·  🏷 ' + esc(matched or ''))
        out.append('💬 ' + _short(text))
        if link:
            out.append('🔗 ' + link)
        out.append('')
        btns = []
        if link:
            btns.append(InlineKeyboardButton(text='🔗 #' + str(lid), url=link))
        if status != 'done':
            btns.append(InlineKeyboardButton(text='✅ #' + str(lid), callback_data='lead:done:' + str(lid)))
        if btns:
            kb_rows.append(btns)
    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton(text='⬅️', callback_data='leadpg:' + str(page - 1)))
    nav.append(InlineKeyboardButton(text=str(page + 1) + '/' + str(pages), callback_data='leadpg:' + str(page)))
    if page < pages - 1:
        nav.append(InlineKeyboardButton(text='➡️', callback_data='leadpg:' + str(page + 1)))
    kb_rows.append(nav)
    kb_rows.append([InlineKeyboardButton(text='⬅️ Админ-меню', callback_data='adm:menu')])
    return NL.join(out), InlineKeyboardMarkup(inline_keyboard=kb_rows)


@admin_router.message(Command('leads'))
async def cmd_leads(message: Message):
    text, kb = await render_leads(0)
    await message.answer(text, reply_markup=kb, disable_web_page_preview=True)


@admin_router.callback_query(F.data.startswith('leadpg:'))
async def cb_leadpg(cb: CallbackQuery):
    page = int(cb.data.split(':')[1])
    text, kb = await render_leads(page)
    try:
        await cb.message.edit_text(text, reply_markup=kb, disable_web_page_preview=True)
    except Exception:
        pass
    await cb.answer()


@admin_router.callback_query(F.data.startswith('lead:done:'))
async def cb_lead_done(cb: CallbackQuery):
    lead_id = int(cb.data.split(':')[2])
    await db.set_lead_status(lead_id, 'done')
    text, kb = await render_leads(0)
    try:
        await cb.message.edit_text(text, reply_markup=kb, disable_web_page_preview=True)
    except Exception:
        pass
    await cb.answer('✅')
