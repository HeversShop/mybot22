"""Configuration for Oncedshop bot."""
import os
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

BOT_TOKEN        = os.getenv('BOT_TOKEN', '')
WEBAPP_URL       = os.getenv('WEBAPP_URL', '').strip()
SUPPORT_USERNAME = os.getenv('SUPPORT_USERNAME', 'oncedshopsupport').lstrip('@')
SUPPORT_URL      = 'https://t.me/' + SUPPORT_USERNAME
DB_PATH          = os.getenv('DB_PATH', 'oncedshop.db')

# ---- Financials ----
PRICE_MARKUP   = 0.12
USD_TO_RUB     = 95.0
STARS_PER_RUB  = 0.9
# Catalog is Standoff 2 Gold only (max item ~$6.38) — keep the minimum below
# the cheapest item or checkout would be impossible for any single purchase.
MIN_ORDER_USD  = 0.3

# ---- Throttling ----
THROTTLE_RATE_SECONDS = 0.7

# ---- New-product notifications scheduler (3-12 hours) ----
NOTIFY_MIN_SEC = 3 * 3600
NOTIFY_MAX_SEC = 12 * 3600

# ---- CryptoBot / CryptoPay ----
# Default invoice/checkout link for "pay via CryptoBot". The admin can change the
# active link at any time with /score <link> (stored in the DB settings table).
CRYPTOBOT_URL = os.getenv('CRYPTOBOT_URL', 'https://t.me/send?start=IVLj8IAey59Z').strip()
CRYPTO_PAY_TOKEN = os.getenv('CRYPTO_PAY_TOKEN', '').strip()
CRYPTO_PAY_TESTNET = os.getenv('CRYPTO_PAY_TESTNET', '0') == '1'

# ---- Crypto wallets ----
CRYPTO_WALLETS = {
    'TON': {
        'address': 'UQDEvKC6YHjTxgq8nsJyK33LRPcqHUEtgebTIM1oPGyPzKs2',
        'usd': 5.50, 'dp': 4, 'emoji': '\U0001f48e', 'label': 'TON',
    },
    'USDT_TRC20': {
        'address': 'TTaXvZ3g9qnLnEGKd9NBP6CNrH5tk35eB6',
        'usd': 1.00, 'dp': 2, 'emoji': '\U0001f7e2', 'label': 'USDT (TRC20)',
    },
    'USDT_ERC20': {
        'address': '0x532689544E299bF588fd17C5805f1eA8bF5A4AF1',
        'usd': 1.00, 'dp': 2, 'emoji': '\U0001f537', 'label': 'USDT (ERC20)',
    },
    'SOL': {
        'address': 'EEBe7mg1e69BDxvuazFjHASK12Pjsu1EZNZFAMjbnTYT',
        'usd': 145.0, 'dp': 4, 'emoji': '\U0001f7e3', 'label': 'Solana',
    },
    'BTC': {
        'address': 'bc1qc7j2jnt3sdrnwhkf9l3uudjan3y3qjjuv0park',
        'usd': 65000.0, 'dp': 8, 'emoji': '\U0001f7e0', 'label': 'Bitcoin',
    },
    'BNB_BEP20': {
        'address': '0xE1a98Db3060D6803c7CA220BB00fF74e420515b9',
        'usd': 600.0, 'dp': 5, 'emoji': '\U0001f7e1', 'label': 'BNB (BEP20)',
    },
}

# ---- Admin ----
ADMIN_USERNAME = os.getenv('ADMIN_USERNAME', 'oncedshopsupport').lstrip('@').lower()
_admin_ids = os.getenv('ADMIN_IDS', '')
ADMIN_IDS = set(int(x) for x in _admin_ids.replace(' ', '').split(',') if x.strip().lstrip('-').isdigit())

_support_chat = os.getenv('SUPPORT_CHAT_ID', '').strip()
SUPPORT_CHAT_ID = int(_support_chat) if _support_chat.lstrip('-').isdigit() else 0

# ---- Web server ----
PORT          = int(os.getenv('PORT', '8080'))
RUN_WEBSERVER = os.getenv('RUN_WEBSERVER', '1') not in ('0', 'false', 'False', 'no', '')
WEBAPP_ORIGIN = os.getenv('WEBAPP_ORIGIN', '*')

# ---- Telethon monitor ----
TG_API_ID      = int(os.getenv('TG_API_ID', '0') or '0')
TG_API_HASH    = os.getenv('TG_API_HASH', '')
TG_SESSION     = os.getenv('TG_SESSION', '')
MONITOR_CHATS  = [c.strip() for c in os.getenv('MONITOR_CHATS', 'FunPayPlace').split(',') if c.strip()]
MONITOR_TRIGGERS = [t.strip().lower() for t in os.getenv(
    'MONITOR_TRIGGERS', '\u043f\u043e\u0441\u0442\u0430\u0432\u0449\u0438\u043a,\u043f\u043e\u0441\u0442\u0430\u0432,#\u0438\u0449\u0443,#\u043a\u0443\u043f\u043b\u044e').split(',') if t.strip()]
MONITOR_NOTIFY_ADMIN = os.getenv('MONITOR_NOTIFY_ADMIN', '1') not in ('0', 'false', 'False', 'no', '')
