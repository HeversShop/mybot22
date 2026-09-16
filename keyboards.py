"""Keyboards for Oncedshop."""
from aiogram.types import (
    InlineKeyboardMarkup, InlineKeyboardButton,
    ReplyKeyboardMarkup, KeyboardButton, WebAppInfo,
)
from config import WEBAPP_URL, CRYPTO_WALLETS
from catalog import CATALOG
from utils import tt

# Reply-keyboard labels (used by exact-match filters in handlers)
BTN_SHOP    = {'ru': '🛒 Магазин',   'en': '🛒 Shop'}
BTN_CATALOG = {'ru': '📎 Каталог',   'en': '📎 Catalog'}
BTN_CART    = {'ru': '♥ Корзина',    'en': '♥ Cart'}
BTN_SUPPORT = {'ru': '📨 Поддержка', 'en': '📨 Support'}
BTN_ORDERS  = {'ru': '📋 Заказы',    'en': '📋 Orders'}

CATALOG_LABELS = set(BTN_CATALOG.values())
CART_LABELS    = set(BTN_CART.values())
SUPPORT_LABELS = set(BTN_SUPPORT.values())
ORDERS_LABELS  = set(BTN_ORDERS.values())
ALL_MENU_LABELS = (CATALOG_LABELS | CART_LABELS | SUPPORT_LABELS | ORDERS_LABELS | set(BTN_SHOP.values()))


def lang_kb():
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text='🇷🇺 Русский', callback_data='lang:ru'),
        InlineKeyboardButton(text='🇬🇧 English',  callback_data='lang:en'),
    ]])


def main_reply_kb(lang='ru'):
    lang = 'ru' if lang == 'ru' else 'en'
    rows = []
    if WEBAPP_URL:
        rows.append([KeyboardButton(text=BTN_SHOP[lang], web_app=WebAppInfo(url=WEBAPP_URL))])
    rows.append([KeyboardButton(text=BTN_CATALOG[lang]), KeyboardButton(text=BTN_CART[lang])])
    rows.append([KeyboardButton(text=BTN_ORDERS[lang]),  KeyboardButton(text=BTN_SUPPORT[lang])])
    return ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True)


def payment_kb(order_id, lang='ru'):
    ru = lang == 'ru'
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='💰 С баланса'            if ru else '💰 From balance',   callback_data='pay:balance:' + order_id)],
        [InlineKeyboardButton(text='⭐ Telegram Stars',                                              callback_data='pay:stars:'   + order_id)],
        [InlineKeyboardButton(text='🪙 Криптовалюта'          if ru else '🪙 Crypto',        callback_data='pay:crypto:'  + order_id)],
        [InlineKeyboardButton(text='🤖 CryptoBot',                                              callback_data='pay:cbot:'   + order_id)],
        [InlineKeyboardButton(text='👤 Оплата у поддержки'  if ru else '👤 Pay via support', callback_data='pay:support:' + order_id)],
    ])


def crypto_kb(order_id, lang='ru'):
    rows = []
    for code, w in CRYPTO_WALLETS.items():
        rows.append([InlineKeyboardButton(text=w['emoji'] + ' ' + w['label'],
                                          callback_data='coin:' + code + ':' + order_id)])
    back = '⬅️ Назад' if lang == 'ru' else '⬅️ Back'
    rows.append([InlineKeyboardButton(text=back, callback_data='pay:back:' + order_id)])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def support_user_kb(lang='ru'):
    '''Shown to the customer under support prompts.'''
    ru = lang == 'ru'
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='📋 Мои заказы' if ru else '📋 My orders', callback_data='sup:myorders')],
    ])
