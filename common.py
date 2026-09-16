'''Shared helpers: admin detection, notification targets, HTML escaping.'''
from aiogram.filters import BaseFilter
from aiogram.types import Message, CallbackQuery

from config import ADMIN_USERNAME, ADMIN_IDS, SUPPORT_CHAT_ID

NL = chr(10)


def esc(text):
    '''Escape text for Telegram HTML parse mode.'''
    return (str(text or '')
            .replace('&', '&amp;')
            .replace('<', '&lt;')
            .replace('>', '&gt;'))


def is_admin(user, chat=None):
    '''True if the Telegram user is an admin.

    Anyone writing from inside SUPPORT_CHAT_ID (the staff group) is treated as
    admin so the whole team can answer customers from one chat.'''
    if chat is not None and SUPPORT_CHAT_ID and chat.id == SUPPORT_CHAT_ID:
        return True
    if user is None:
        return False
    if user.id in ADMIN_IDS:
        return True
    return bool(ADMIN_USERNAME) and (user.username or '').lower() == ADMIN_USERNAME


def user_label(user_id, username=None, full_name=None):
    '''Human-friendly label for a customer.'''
    if username:
        return '@' + username
    if full_name:
        return full_name
    return 'id' + str(user_id)


def admin_targets():
    '''Chats that should receive staff notifications (support group + admins).'''
    targets = []
    if SUPPORT_CHAT_ID:
        targets.append(SUPPORT_CHAT_ID)
    for aid in ADMIN_IDS:
        if aid not in targets:
            targets.append(aid)
    return targets


def support_inbox_targets():
    '''Where customer messages are delivered: the support group if configured,
    otherwise every admin in private.'''
    if SUPPORT_CHAT_ID:
        return [SUPPORT_CHAT_ID]
    return list(ADMIN_IDS)


class IsAdmin(BaseFilter):
    async def __call__(self, event):
        if isinstance(event, Message):
            return is_admin(event.from_user, event.chat)
        if isinstance(event, CallbackQuery):
            chat = event.message.chat if event.message else None
            return is_admin(event.from_user, chat)
        return False


class NotAdmin(BaseFilter):
    async def __call__(self, event):
        if isinstance(event, Message):
            return not is_admin(event.from_user, event.chat)
        if isinstance(event, CallbackQuery):
            chat = event.message.chat if event.message else None
            return not is_admin(event.from_user, chat)
        return True


class IsPrivate(BaseFilter):
    async def __call__(self, event):
        if isinstance(event, Message):
            return event.chat.type == 'private'
        if isinstance(event, CallbackQuery):
            return bool(event.message) and event.message.chat.type == 'private'
        return False
