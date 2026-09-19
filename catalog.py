'''Product catalog for Hevers Shop. Base prices in USD; +12% markup applied in utils.'''

CATALOG = [
    {'id': 'stars', 'emoji': '⭐', 'title': {'ru': 'Telegram Stars', 'en': 'Telegram Stars'}, 'items': [
        {'id': 'p_stars_1k', 'emoji': '⭐', 'title': {'ru': 'Telegram Stars', 'en': 'Telegram Stars'},
         'kind': 'per1000', 'base': 12.0, 'unit': 'Stars', 'step': 500, 'def': 1000, 'min': 1},
    ]},
    {'id': 'tiktok', 'emoji': '📱', 'title': {'ru': 'TikTok Монеты', 'en': 'TikTok Coins'}, 'items': [
        {'id': 'p_tt_coins', 'emoji': '🪙', 'title': {'ru': 'TikTok Монеты', 'en': 'TikTok Coins'},
         'kind': 'per1000', 'base': 11.05, 'unit': 'Монет', 'step': 100, 'def': 100, 'min': 1,
         'note': {'ru': 'Вход на аккаунт (1.05р/шт)', 'en': 'Account login (1.05 RUB/pc)'}},
    ]},
    {'id': 'rbx', 'emoji': '🟩', 'title': {'ru': 'Roblox Robux', 'en': 'Roblox Robux'}, 'items': [
        {'id': 'p_rbxgp_new', 'emoji': '🟦', 'title': {'ru': 'Robux GamePass', 'en': 'Robux GamePass'},
         'kind': 'per1000', 'base': 3.6, 'unit': 'R$', 'step': 1000, 'def': 1000, 'min': 1000,
         'note': {'ru': 'Выдача 5 дней', 'en': '5 days delivery'}},
        {'id': 'p_rbxpv_new', 'emoji': '🟪', 'title': {'ru': 'Robux Private Server', 'en': 'Robux Private Server'},
         'kind': 'per1000', 'base': 3.0, 'unit': 'R$', 'step': 1000, 'def': 1000, 'min': 1000,
         'note': {'ru': 'Выдача 5 дней', 'en': '5 days delivery'}},
    ]},
    {'id': 'brawl', 'emoji': '🎮', 'title': {'ru': 'Brawl Stars', 'en': 'Brawl Stars'}, 'items': [
        {'id': 'p_brawl_pass', 'emoji': '🎮', 'title': {'ru': 'Brawl Pass', 'en': 'Brawl Pass'},
         'kind': 'fixed', 'price': 3.15, 'note': {'ru': '300 рублей', 'en': '300 RUB'}},
        {'id': 'p_brawl_plus_new', 'emoji': '🎮', 'title': {'ru': 'Brawl Pass Plus', 'en': 'Brawl Pass Plus'},
         'kind': 'fixed', 'price': 3.68, 'note': {'ru': '350 рублей', 'en': '350 RUB'}},
    ]},
    {'id': 'ai', 'emoji': '🤖', 'title': {'ru': 'AI Подписки', 'en': 'AI Subscriptions'}, 'items': [
        {'id': 'p_gpt_plus_180', 'emoji': '💬', 'title': {'ru': 'ChatGPT Plus (Личный)', 'en': 'ChatGPT Plus (Personal)'},
         'kind': 'fixed', 'price': 1.89, 'note': {'ru': '180 рублей / Гарантия', 'en': '180 RUB / Warranty'}},
        {'id': 'p_gpt_plus_300', 'emoji': '💬', 'title': {'ru': 'ChatGPT Plus (Аккаунт)', 'en': 'ChatGPT Plus (Account)'},
         'kind': 'fixed', 'price': 3.15, 'note': {'ru': '300 рублей / Гарантия', 'en': '300 RUB / Warranty'}},
        {'id': 'p_gemini_18m', 'emoji': '✨', 'title': {'ru': 'Gemini 18 мес (Аккаунт)', 'en': 'Gemini 18m (Account)'},
         'kind': 'fixed', 'price': 1.05, 'note': {'ru': '100 рублей / Гарантия', 'en': '100 RUB / Warranty'}},
        {'id': 'p_grok_300', 'emoji': '✖️', 'title': {'ru': 'Super Grok 1 мес', 'en': 'Super Grok 1m'},
         'kind': 'fixed', 'price': 3.15, 'note': {'ru': '300 рублей / Гарантия', 'en': '300 RUB / Warranty'}},
        {'id': 'p_claude_30d', 'emoji': '🧠', 'title': {'ru': 'Claude PRO 30 дней', 'en': 'Claude PRO 30 days'},
         'kind': 'fixed', 'price': 3.15, 'note': {'ru': '300 рублей', 'en': '300 RUB'}},
        {'id': 'p_claude_365d', 'emoji': '🧠', 'title': {'ru': 'Claude PRO 365 дней', 'en': 'Claude PRO 365 days'},
         'kind': 'fixed', 'price': 15.79, 'note': {'ru': '1500 рублей', 'en': '1500 RUB'}},
    ]},
    {'id': 'virta', 'emoji': '💰', 'title': {'ru': 'Игровая Валюта', 'en': 'Game Currency'}, 'items': [
        {'id': 'p_radmir', 'emoji': '🚗', 'title': {'ru': 'Radmir Вирты', 'en': 'Radmir Virts'},
         'kind': 'per1000', 'base': 0.55, 'unit': '1kk', 'step': 1, 'def': 25, 'min': 25,
         'note': {'ru': '52р за 1кк', 'en': '52 RUB per 1m'}},
        {'id': 'p_amazing', 'emoji': '🚗', 'title': {'ru': 'Amazing Вирты', 'en': 'Amazing Virts'},
         'kind': 'per1000', 'base': 0.47, 'unit': '1kk', 'step': 1, 'def': 25, 'min': 25,
         'note': {'ru': '45р за 1кк', 'en': '45 RUB per 1m'}},
        {'id': 'p_black_russia', 'emoji': '🚗', 'title': {'ru': 'Black Russia Вирты', 'en': 'Black Russia Virts'},
         'kind': 'per1000', 'base': 0.37, 'unit': '1kk', 'step': 1, 'def': 30, 'min': 30,
         'note': {'ru': '35р за 1кк', 'en': '35 RUB per 1m'}},
        {'id': 'p_majestic', 'emoji': '🚗', 'title': {'ru': 'Majestic Вирты', 'en': 'Majestic Virts'},
         'kind': 'per1000', 'base': 2.11, 'unit': '1kk', 'step': 1, 'def': 25, 'min': 25,
         'note': {'ru': '0.20р за 1к (200р за 1кк)', 'en': '0.20 RUB per 1k'}},
        {'id': 'p_arizona', 'emoji': '🚗', 'title': {'ru': 'Arizona RP Вирты', 'en': 'Arizona RP Virts'},
         'kind': 'per1000', 'base': 2.63, 'unit': '1kkk', 'step': 1, 'def': 1, 'min': 1,
         'note': {'ru': '0.25р за 1кк (250р за 1ккк)', 'en': '0.25 RUB per 1m'}},
    ]},
]


def all_products():
    out = []
    for cat in CATALOG:
        for p in cat.get('items', []):
            out.append(p)
    return out


def find_product(pid):
    for cat in CATALOG:
        for p in cat.get('items', []):
            if p['id'] == pid:
                return p
    return None
