'''In-bot support chat.

Customer side  (support_router, attached LAST):
    Any message a customer sends that no other handler consumed is delivered
    to the staff (SUPPORT_CHAT_ID group or every admin in private) with a
    header + inline buttons. Media is copied as-is.

Staff side (staff_router, attached FIRST, IsAdmin at router level):
    * Reply (swipe) to a delivered customer message  -> goes to that customer
    * Press "Ответить" (or /reply <id|@user>)        -> sticky mode: every next
      message goes to that customer until /stop or "Завершить"
    * /tickets, /history <id>, /close [id]
'''
import logging

from aiogram import Router, F, Bot
from aiogram.filters import Command, CommandObject, BaseFilter
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, ReactionTypeEmoji
from aiogram.exceptions import TelegramForbiddenError, TelegramBadRequest

import database as db
from common import (
    NL, esc, is_admin, user_label, support_inbox_targets,
    IsAdmin, NotAdmin, IsPrivate,
)
from keyboards import SUPPORT_LABELS, ALL_MENU_LABELS, support_user_kb, main_reply_kb

log = logging.getLogger(__name__)

support_router = Router(name='support_customer')
staff_router = Router(name='support_staff')
staff_router.message.filter(IsAdmin())
staff_router.callback_query.filter(IsAdmin())

# admin_id -> customer user_id (sticky reply mode)
REPLY_TARGET = {}

TICKETS_PER_PAGE = 8
_CAPTIONABLE = ('photo', 'video', 'document', 'audio', 'animation')


def R(lang):
    return lang == 'ru'


# ─────────────────────────── keyboards ────────────────────────────────────────
def staff_reply_kb(user_id, order_id=None, closed=False):
    uid = str(user_id)
    rows = [[
        InlineKeyboardButton(text='✉️ Ответить', callback_data='sup:reply:' + uid),
        InlineKeyboardButton(text='🕘 История', callback_data='sup:hist:' + uid),
    ], [
        InlineKeyboardButton(text='🧾 Заказы клиента', callback_data='sup:orders:' + uid),
        InlineKeyboardButton(text='✅ Закрыто' if closed else '🔒 Закрыть',
                             callback_data='sup:noop' if closed else 'sup:close:' + uid),
    ]]
    if order_id:
        rows.insert(0, [InlineKeyboardButton(text='📦 Выдан · ' + order_id,
                                             callback_data='adm:odone:' + order_id + ':' + uid)])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def reply_mode_kb(user_id):
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text='⏹ Завершить режим ответа', callback_data='sup:stop'),
        InlineKeyboardButton(text='🔒 Закрыть обращение', callback_data='sup:close:' + str(user_id)),
    ]])


# ─────────────────────────── helpers ──────────────────────────────────────────
def _content_label(message: Message):
    for attr, lbl in (('photo', '🖼 Фото'), ('video', '🎬 Видео'), ('document', '📎 Файл'),
                      ('voice', '🎤 Голосовое'), ('audio', '🎵 Аудио'), ('sticker', '🩷 Стикер'),
                      ('animation', '🎞 GIF'), ('video_note', '📹 Кружок'), ('location', '📍 Локация'),
                      ('contact', '👤 Контакт')):
        if getattr(message, attr, None):
            return lbl
    return '💬 Сообщение'


def _plain_text(message: Message):
    return message.text or message.caption or ''


async def _label_for(user_id):
    u = await db.get_user(user_id)
    if u:
        return user_label(user_id, u.get('username'), u.get('full_name'))
    return 'id' + str(user_id)


async def deliver_to_staff(bot: Bot, message: Message, order_id=None, note=None):
    '''Copy a customer message to the staff inbox and remember the mapping.'''
    u = message.from_user
    await db.upsert_user(u.id, u.username or '', u.full_name or '')
    label = user_label(u.id, u.username, u.full_name)
    ticket = await db.ticket_get(u.id)
    is_new = (ticket is None) or ticket.get('status') != 'open' or ticket.get('last_from') == 'admin'

    header = ('🆕 ' if is_new else '💬 ') + '<b>Сообщение от клиента</b>' + NL
    header += '👤 ' + esc(label) + ' · id<code>' + str(u.id) + '</code>'
    if u.username:
        header += ' · <a href="tg://user?id=' + str(u.id) + '">профиль</a>'
    if note:
        header += NL + note
    kb = staff_reply_kb(u.id, order_id)

    delivered = 0
    for chat_id in support_inbox_targets():
        try:
            if message.text:
                sent = await bot.send_message(chat_id, header + NL + NL + message.html_text,
                                              reply_markup=kb, disable_web_page_preview=True)
                await db.support_map_put(chat_id, sent.message_id, u.id)
            else:
                sent = await bot.send_message(chat_id, header + NL + _content_label(message) + ' ⬇️',
                                              reply_markup=kb)
                await db.support_map_put(chat_id, sent.message_id, u.id)
                copied = await bot.copy_message(chat_id, message.chat.id, message.message_id)
                await db.support_map_put(chat_id, copied.message_id, u.id)
            delivered += 1
        except Exception as e:
            log.warning('deliver_to_staff -> %s failed: %s', chat_id, e)

    await db.ticket_touch(u.id, 'in', _plain_text(message) or _content_label(message))
    return delivered, is_new


async def send_to_customer(bot: Bot, message: Message, user_id: int):
    '''Deliver a staff message to the customer. Returns (ok, error_text).'''
    lang = await db.get_language(user_id)
    prefix = '💬 <b>Поддержка Oncedshop</b>' if R(lang) else '💬 <b>Oncedshop Support</b>'
    try:
        if message.text:
            await bot.send_message(user_id, prefix + NL + NL + message.html_text,
                                   disable_web_page_preview=True)
        elif message.content_type in _CAPTIONABLE:
            cap = prefix + ((NL + NL + message.html_text) if message.caption else '')
            await bot.copy_message(user_id, message.chat.id, message.message_id, caption=cap[:1024])
        else:
            await bot.send_message(user_id, prefix)
            await bot.copy_message(user_id, message.chat.id, message.message_id)
    except TelegramForbiddenError:
        return False, '❌ Клиент заблокировал бота — сообщение не доставлено.'
    except TelegramBadRequest as e:
        if 'chat not found' in str(e).lower():
            return False, '❌ Клиент ещё не писал боту (chat not found).'
        return False, '❌ Не удалось отправить: ' + esc(e)
    except Exception as e:
        log.exception('send_to_customer: %s', e)
        return False, '❌ Ошибка отправки: ' + esc(e)
    await db.ticket_touch(user_id, 'out', _plain_text(message) or _content_label(message),
                          admin_id=message.from_user.id)
    return True, ''


async def notify_staff(bot: Bot, text, user_id=None, order_id=None):
    '''Send a system notification (new order, payment...) to the staff inbox.'''
    kb = staff_reply_kb(user_id, order_id) if user_id else None
    for chat_id in support_inbox_targets():
        try:
            sent = await bot.send_message(chat_id, text, reply_markup=kb, disable_web_page_preview=True)
            if user_id:
                await db.support_map_put(chat_id, sent.message_id, user_id)
        except Exception as e:
            log.warning('notify_staff -> %s failed: %s', chat_id, e)


async def render_tickets(page=0):
    total = await db.tickets_count('open')
    pages = max(1, (total + TICKETS_PER_PAGE - 1) // TICKETS_PER_PAGE)
    page = max(0, min(page, pages - 1))
    rows = await db.tickets_list('open', TICKETS_PER_PAGE, page * TICKETS_PER_PAGE)
    out = ['📨 <b>Обращения в поддержку</b>', 'Открытых: ' + str(total), '']
    kb_rows = []
    if not rows:
        out.append('Открытых обращений нет.')
    for t in rows:
        uid = t['user_id']
        label = user_label(uid, t.get('username'), t.get('full_name'))
        unread = int(t.get('unread') or 0)
        mark = ('🔴 ' + str(unread) + ' ') if unread else '⚪️ '
        who = 'клиент' if t.get('last_from') == 'user' else 'вы'
        out.append(mark + '<b>' + esc(label) + '</b> · id<code>' + str(uid) + '</code>')
        out.append('   ' + who + ': ' + esc((t.get('last_text') or '')[:90]))
        kb_rows.append([
            InlineKeyboardButton(text='✉️ ' + label[:20], callback_data='sup:reply:' + str(uid)),
            InlineKeyboardButton(text='🕘', callback_data='sup:hist:' + str(uid)),
            InlineKeyboardButton(text='🔒', callback_data='sup:close:' + str(uid)),
        ])
    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton(text='⬅️', callback_data='sup:list:' + str(page - 1)))
    nav.append(InlineKeyboardButton(text=str(page + 1) + '/' + str(pages), callback_data='sup:list:' + str(page)))
    if page < pages - 1:
        nav.append(InlineKeyboardButton(text='➡️', callback_data='sup:list:' + str(page + 1)))
    kb_rows.append(nav)
    kb_rows.append([InlineKeyboardButton(text='⬅️ Админ-меню', callback_data='adm:menu')])
    return NL.join(out), InlineKeyboardMarkup(inline_keyboard=kb_rows)


async def render_history(user_id, limit=15):
    label = await _label_for(user_id)
    rows = await db.support_history(user_id, limit)
    out = ['🕘 <b>История с ' + esc(label) + '</b> (id<code>' + str(user_id) + '</code>)', '']
    if not rows:
        out.append('Сообщений пока нет.')
    for direction, admin_id, text, created in rows:
        who = '👤' if direction == 'in' else '🛠'
        ts = (created or '')[5:16].replace('T', ' ')
        out.append(who + ' <i>' + ts + '</i> ' + esc((text or '')[:200]))
    return NL.join(out)


async def _resolve_user(query):
    '''"123456" or "@name" -> user_id or None.'''
    q = str(query or '').strip()
    if not q:
        return None
    if q.lstrip('-').isdigit():
        return int(q)
    u = await db.find_user(q)
    return int(u['user_id']) if u else None


async def enter_reply_mode(target: Message, admin_id: int, user_id: int):
    REPLY_TARGET[admin_id] = user_id
    label = await _label_for(user_id)
    await target.answer(
        '✉️ <b>Режим ответа:</b> ' + esc(label) + ' (id<code>' + str(user_id) + '</code>)' + NL +
        'Всё, что вы напишете сюда (текст, фото, файлы), уйдёт этому клиенту.' + NL +
        'Выйти: кнопка ниже или /stop.',
        reply_markup=reply_mode_kb(user_id),
    )


# ─────────────────────────── staff: filters ───────────────────────────────────
class StaffReplyFilter(BaseFilter):
    '''Matches a staff message that should be forwarded to a customer.'''
    async def __call__(self, message: Message):
        if message.text and message.text.startswith('/'):
            return False
        if message.text and message.text in ALL_MENU_LABELS:
            return False
        if message.reply_to_message:
            uid = await db.support_map_get(message.chat.id, message.reply_to_message.message_id)
            if uid:
                return {'target_user_id': uid}
        uid = REPLY_TARGET.get(message.from_user.id)
        if uid:
            return {'target_user_id': uid}
        return False


# ─────────────────────────── staff: handlers ──────────────────────────────────
@staff_router.message(StaffReplyFilter())
async def staff_reply(message: Message, target_user_id: int):
    ok, err = await send_to_customer(message.bot, message, target_user_id)
    label = await _label_for(target_user_id)
    if ok:
        try:
            await message.react([ReactionTypeEmoji(emoji='👍')])
        except Exception:
            await message.reply('✅ Отправлено → ' + esc(label))
    else:
        await message.reply(err)


@staff_router.message(Command('reply', 'r'))
async def cmd_reply(message: Message, command: CommandObject):
    uid = await _resolve_user(command.args)
    if not uid:
        await message.answer('Использование: <code>/reply 123456789</code> или <code>/reply @username</code>')
        return
    await enter_reply_mode(message, message.from_user.id, uid)


@staff_router.message(Command('stop'))
async def cmd_stop(message: Message):
    if REPLY_TARGET.pop(message.from_user.id, None):
        await message.answer('⏹ Режим ответа выключен.')
    else:
        await message.answer('Режим ответа и так не активен.')


@staff_router.message(Command('close'))
async def cmd_close(message: Message, command: CommandObject):
    uid = await _resolve_user(command.args) or REPLY_TARGET.get(message.from_user.id)
    if not uid:
        await message.answer('Использование: <code>/close 123456789</code> (или в режиме ответа просто /close)')
        return
    await _close_ticket(message.bot, uid)
    REPLY_TARGET.pop(message.from_user.id, None)
    await message.answer('🔒 Обращение id' + str(uid) + ' закрыто.')


@staff_router.message(Command('tickets'))
async def cmd_tickets(message: Message):
    text, kb = await render_tickets(0)
    await message.answer(text, reply_markup=kb)


@staff_router.message(Command('history', 'h'))
async def cmd_history(message: Message, command: CommandObject):
    uid = await _resolve_user(command.args) or REPLY_TARGET.get(message.from_user.id)
    if not uid:
        await message.answer('Использование: <code>/history 123456789</code>')
        return
    await message.answer(await render_history(uid))


async def _close_ticket(bot: Bot, user_id: int):
    await db.ticket_close(user_id)
    lang = await db.get_language(user_id)
    try:
        await bot.send_message(
            user_id,
            ('🔒 Обращение закрыто. Если появятся вопросы — просто напишите сюда.' if R(lang)
             else '🔒 Your request has been closed. Feel free to write again anytime.'),
            reply_markup=main_reply_kb(lang),
        )
    except Exception:
        pass


@staff_router.callback_query(F.data.startswith('sup:reply:'))
async def cb_reply(cb: CallbackQuery):
    uid = int(cb.data.split(':')[2])
    await enter_reply_mode(cb.message, cb.from_user.id, uid)
    await cb.answer()


@staff_router.callback_query(F.data == 'sup:stop')
async def cb_stop(cb: CallbackQuery):
    REPLY_TARGET.pop(cb.from_user.id, None)
    try:
        await cb.message.edit_text('⏹ Режим ответа выключен.')
    except Exception:
        pass
    await cb.answer('Выключено')


@staff_router.callback_query(F.data.startswith('sup:close:'))
async def cb_close(cb: CallbackQuery):
    uid = int(cb.data.split(':')[2])
    await _close_ticket(cb.bot, uid)
    if REPLY_TARGET.get(cb.from_user.id) == uid:
        REPLY_TARGET.pop(cb.from_user.id, None)
    try:
        await cb.message.edit_reply_markup(reply_markup=staff_reply_kb(uid, closed=True))
    except Exception:
        pass
    await cb.answer('🔒 Закрыто')


@staff_router.callback_query(F.data.startswith('sup:hist:'))
async def cb_hist(cb: CallbackQuery):
    uid = int(cb.data.split(':')[2])
    await cb.message.answer(await render_history(uid), reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text='✉️ Ответить', callback_data='sup:reply:' + str(uid)),
        InlineKeyboardButton(text='🧾 Заказы', callback_data='sup:orders:' + str(uid)),
    ]]))
    await cb.answer()


@staff_router.callback_query(F.data.startswith('sup:orders:'))
async def cb_user_orders(cb: CallbackQuery):
    uid = int(cb.data.split(':')[2])
    from admin import render_user_orders
    text, kb = await render_user_orders(uid)
    await cb.message.answer(text, reply_markup=kb)
    await cb.answer()


@staff_router.callback_query(F.data.startswith('sup:list:'))
async def cb_list(cb: CallbackQuery):
    page = int(cb.data.split(':')[2])
    text, kb = await render_tickets(page)
    try:
        await cb.message.edit_text(text, reply_markup=kb)
    except Exception:
        await cb.message.answer(text, reply_markup=kb)
    await cb.answer()


@staff_router.callback_query(F.data == 'sup:noop')
async def cb_noop(cb: CallbackQuery):
    await cb.answer()


# ─────────────────────────── customer: handlers ───────────────────────────────
@support_router.message(F.text.in_(SUPPORT_LABELS))
async def support_button(message: Message):
    lang = await db.get_language(message.from_user.id)
    if R(lang):
        txt = ('📨 <b>Поддержка Oncedshop</b>' + NL + NL +
               'Напишите ваш вопрос прямо сюда — текст, скриншот или чек.' + NL +
               'Оператор ответит в этом же чате.')
    else:
        txt = ('📨 <b>Oncedshop Support</b>' + NL + NL +
               'Type your question right here — text, screenshot or receipt.' + NL +
               'An operator will reply in this chat.')
    await message.answer(txt, reply_markup=support_user_kb(lang))


@support_router.callback_query(F.data == 'sup:myorders')
async def cb_myorders(cb: CallbackQuery):
    from handlers import my_orders_text
    lang = await db.get_language(cb.from_user.id)
    await cb.message.answer(await my_orders_text(cb.from_user.id, lang))
    await cb.answer()


@support_router.message(NotAdmin(), IsPrivate(), F.text.startswith('/'))
async def unknown_command(message: Message):
    lang = await db.get_language(message.from_user.id)
    await message.answer('🤷 Неизвестная команда. Меню: /start' if R(lang)
                         else '🤷 Unknown command. Menu: /start',
                         reply_markup=main_reply_kb(lang))


@support_router.message(NotAdmin(), IsPrivate())
async def customer_message(message: Message):
    '''Catch-all: everything else a customer sends goes to support.'''
    lang = await db.get_language(message.from_user.id)
    delivered, is_new = await deliver_to_staff(message.bot, message)
    if not delivered:
        await message.answer('⚠️ Поддержка временно недоступна, попробуйте позже.' if R(lang)
                             else '⚠️ Support is temporarily unavailable, please try again later.')
        return
    if is_new:
        await message.answer('✅ Сообщение передано в поддержку. Ответ придёт сюда.' if R(lang)
                             else '✅ Your message was sent to support. The reply will arrive here.')


@support_router.message(IsAdmin(), IsPrivate())
async def admin_stray(message: Message):
    '''Admin typed something in private that isn't a command/reply.'''
    if message.text and message.text.startswith('/'):
        await message.answer('🤷 Неизвестная команда. Админ-меню: /admin')
        return
    await message.answer(
        'ℹ️ Чтобы ответить клиенту — сделайте <b>reply</b> на его сообщение, '
        'нажмите «✉️ Ответить» под ним или используйте <code>/reply id</code>.' + NL +
        'Список обращений: /tickets · Меню: /admin')
