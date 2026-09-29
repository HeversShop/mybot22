"""New-product notification scheduler.

Sends a broadcast to ALL bot users (except blocked ones) every 3–12 hours.
Categories excluded: 'stars' (Telegram Stars) and 'brawl' (Battle Pass).
"""
import asyncio
import logging
import random

from aiogram import Bot
from aiogram.exceptions import TelegramForbiddenError, TelegramBadRequest

import database as db
from catalog import products_for_notifications, CATALOG
from config import NOTIFY_MIN_SEC, NOTIFY_MAX_SEC, USD_TO_RUB, GOLD_PER_RUB, WEBAPP_URL

log = logging.getLogger('oncedshop.notifier')

_MARKUP = 1.12  # same as PRICE_MARKUP in config


def _pick_items(n: int = 3):
    """Pick n random products from non-excluded categories."""
    pool = products_for_notifications()
    if not pool:
        return []
    random.shuffle(pool)
    return pool[:n]


def _fmt_price(base_usd: float) -> str:
    rub = round(base_usd * _MARKUP * USD_TO_RUB)
    gold = round(rub / GOLD_PER_RUB)
    return f"{rub:,} ₽  |  🪙 {gold:,} Gold"


def _build_message(items) -> str:
    lines = ["🆕 <b>Новые поступления в Oncedshop!</b>\n"]
    for entry in items:
        cat = entry['cat']
        p = entry['product']
        title = p['title'].get('ru', p['title'].get('en', ''))
        cat_name = cat['title'].get('ru', cat['title'].get('en', ''))
        base = p.get('base', p.get('price', 0))
        price_line = _fmt_price(base) if base else ''
        note = ''
        if p.get('note'):
            note = p['note'].get('ru', '') or p['note'].get('en', '')
        lines.append(
            f"{cat['emoji']} <b>{title}</b>  <i>({cat_name})</i>\n"
            f"{'💰 ' + price_line if price_line else ''}"
            f"{chr(10) + '   ' + note if note else ''}"
        )
    if WEBAPP_URL:
        lines.append(f'\n👉 <a href="{WEBAPP_URL}">Открыть магазин</a>')
    else:
        lines.append('\n👉 Нажмите <b>🛒 Магазин</b> в меню бота')
    return '\n\n'.join(lines)


async def _broadcast(bot: Bot, text: str):
    """Send text to all users in DB, skip blocked/deleted accounts."""
    users = await db.get_all_user_ids()
    sent = 0
    failed = 0
    for uid in users:
        try:
            await bot.send_message(uid, text, parse_mode='HTML', disable_web_page_preview=True)
            sent += 1
        except (TelegramForbiddenError, TelegramBadRequest):
            failed += 1
        except Exception as exc:
            log.warning('notify uid=%s: %s', uid, exc)
            failed += 1
        await asyncio.sleep(0.05)  # ~20 msg/s to stay within Telegram limits
    log.info('Broadcast done: sent=%d failed=%d', sent, failed)


async def notify_loop(bot: Bot):
    """Infinite loop: wait random 3–12 h, then broadcast new-product message."""
    while True:
        delay = random.randint(NOTIFY_MIN_SEC, NOTIFY_MAX_SEC)
        log.info('Next notification in %.1f hours', delay / 3600)
        await asyncio.sleep(delay)
        items = _pick_items(3)
        if not items:
            log.warning('No items available for notification (all excluded?)')
            continue
        text = _build_message(items)
        await _broadcast(bot, text)
