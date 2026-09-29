"""Oncedshop bot — entry point (Railway). Web server binds to $PORT first."""
import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import BotCommand, BotCommandScopeChat, BotCommandScopeDefault

from config import BOT_TOKEN, RUN_WEBSERVER, PORT, ADMIN_IDS, SUPPORT_CHAT_ID, WEBAPP_URL
from middlewares import ThrottlingMiddleware
from handlers import router
from shopflow import shop_router
from admin import admin_router
from support import staff_router, support_router
from notifier import notify_loop
import database as db

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(name)s: %(message)s')
log = logging.getLogger('oncedshop')

USER_COMMANDS = [
    BotCommand(command='start',   description='🛒 Главное меню'),
    BotCommand(command='shop',    description='📎 Каталог товаров'),
    BotCommand(command='cart',    description='♥ Моя корзина'),
    BotCommand(command='orders',  description='📋 Мои заказы'),
    BotCommand(command='id',      description='🆔 Мой Telegram ID'),
]

ADMIN_COMMANDS = [
    BotCommand(command='admin',    description='◼️ Админ-панель'),
    BotCommand(command='tickets',  description='📨 Обращения клиентов'),
    BotCommand(command='orders',   description='🧾 Заказы'),
    BotCommand(command='users',    description='👥 Пользователи'),
    BotCommand(command='reply',    description='✉️ Написать клиенту: /reply id'),
    BotCommand(command='stop',     description='⏹ Выйти из режима ответа'),
    BotCommand(command='done',     description='✅ Заказ выдан: /done ONC-XXXX'),
    BotCommand(command='balance',  description='💰 Баланс: /balance id +10'),
    BotCommand(command='discount', description='🏷 Скидка: /discount id 10'),
    BotCommand(command='history',  description='🕘 История: /history id'),
    BotCommand(command='close',    description='🔒 Закрыть обращение'),
    BotCommand(command='leads',    description='🎯 Лиды из чатов'),
    BotCommand(command='id',       description='🆔 Мой Telegram ID'),
]


async def setup_commands(bot: Bot):
    try:
        await bot.set_my_commands(USER_COMMANDS, scope=BotCommandScopeDefault())
    except Exception as e:
        log.warning('set_my_commands(default): %s', e)
    targets = set(ADMIN_IDS)
    if SUPPORT_CHAT_ID:
        targets.add(SUPPORT_CHAT_ID)
    for chat_id in targets:
        try:
            await bot.set_my_commands(ADMIN_COMMANDS, scope=BotCommandScopeChat(chat_id=chat_id))
        except Exception as e:
            log.warning('set_my_commands(%s): %s', chat_id, e)


async def main():
    try:
        await db.init_db()
        log.info('DB ready: %s', db.DB_PATH)
    except Exception as e:
        log.exception('db init failed: %s', e)

    bot = None
    if BOT_TOKEN:
        bot = Bot(BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
        log.info('BOT_TOKEN is set; Telegram polling will be started.')
    else:
        log.error('BOT_TOKEN is not set. Set it in Railway › Variables. The bot cannot answer /start.')

    if not ADMIN_IDS and not SUPPORT_CHAT_ID:
        log.warning('ADMIN_IDS / SUPPORT_CHAT_ID are empty — customer messages have nowhere to go. '
                    'Send /id to the bot and put your id into ADMIN_IDS.')
    if not WEBAPP_URL:
        log.warning('WEBAPP_URL is empty — the "Shop" mini-app button is hidden (catalog still works).')

    runner = None
    if RUN_WEBSERVER:
        try:
            from server import start_webserver
            runner = await start_webserver(bot)
            log.info('Web server bound to 0.0.0.0:%s', PORT)
        except Exception as e:
            log.exception('web server failed: %s', e)

    if not BOT_TOKEN:
        try:
            while True:
                await asyncio.sleep(3600)
        finally:
            if runner:
                await runner.cleanup()
        return

    dp = Dispatcher()
    dp.message.middleware(ThrottlingMiddleware())
    dp.callback_query.middleware(ThrottlingMiddleware())

    # Order matters:
    #   staff_router   – admin replies to customers (reply / sticky mode)
    #   admin_router   – /admin, /orders, /users ... (IsAdmin at router level)
    #   router         – customer commands, payments, "my orders"
    #   shop_router    – in-bot catalog & cart
    #   support_router – LAST: anything else from a customer -> support inbox
    dp.include_router(staff_router)
    dp.include_router(admin_router)
    dp.include_router(router)
    dp.include_router(shop_router)
    dp.include_router(support_router)

    log.info('Oncedshop bot starting polling...')
    try:
        me = await bot.get_me()
        log.info('Telegram authorization OK: @%s (id=%s)', me.username, me.id)
        await bot.delete_webhook(drop_pending_updates=True)
        await setup_commands(bot)
        log.info('Polling is active. Send /start to @%s.', me.username)

        # Start new-product notification scheduler (every 3–12 h, no BP/Stars)
        asyncio.create_task(notify_loop(bot))
        log.info('New-product notifier scheduled (3–12 h interval).')

        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        if runner:
            await runner.cleanup()
        await bot.session.close()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        pass
