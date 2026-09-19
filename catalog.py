'''Product catalog for Hevers Shop. Base prices in USD; +12% markup applied in utils.'''

CATALOG = [
    {'id': 'stars', 'emoji': '⭐', 'title': {'ru': 'Telegram Stars', 'en': 'Telegram Stars'}, 'items': [
        {'id': 'p_stars_1k', 'img': 'https://raw.githubusercontent.com/HeversShop/mybot22/main/webapp/icons/stars.png', 'title': {'ru': 'Telegram Stars', 'en': 'Telegram Stars'},
         'kind': 'per1000', 'base': 12.0, 'unit': 'Stars', 'step': 500, 'def': 1000, 'min': 1},
    ]},
    {'id': 'tiktok', 'emoji': '📱', 'title': {'ru': 'TikTok Монеты', 'en': 'TikTok Coins'}, 'items': [
        {'id': 'p_tt_coins', 'img': 'https://raw.githubusercontent.com/HeversShop/mybot22/main/webapp/icons/tiktok.png', 'title': {'ru': 'TikTok Монеты', 'en': 'TikTok Coins'},
         'kind': 'perUnit', 'base': 0.0105, 'unit': 'Монет', 'step': 100, 'def': 100, 'min': 100,
         'note': {'ru': 'Вход на аккаунт (1.05р/шт)', 'en': 'Account login (1.05 RUB/pc)'}},
    ]},
    {'id': 'rbx', 'emoji': '🟩', 'title': {'ru': 'Roblox Robux', 'en': 'Roblox Robux'}, 'items': [
        {'id': 'p_rbxgp_new', 'img': 'https://raw.githubusercontent.com/HeversShop/mybot22/main/webapp/icons/roblox.png', 'title': {'ru': 'Robux GamePass', 'en': 'Robux GamePass'},
         'kind': 'perUnit', 'base': 0.0036, 'unit': 'R$', 'step': 1000, 'def': 1000, 'min': 1000,
         'note': {'ru': 'Выдача 5 дней', 'en': '5 days delivery'}},
        {'id': 'p_rbxpv_new', 'img': 'https://raw.githubusercontent.com/HeversShop/mybot22/main/webapp/icons/roblox.png', 'title': {'ru': 'Robux Private Server', 'en': 'Robux Private Server'},
         'kind': 'perUnit', 'base': 0.003, 'unit': 'R$', 'step': 1000, 'def': 1000, 'min': 1000,
         'note': {'ru': 'Выдача 5 дней', 'en': '5 days delivery'}},
    ]},
    {'id': 'brawl', 'emoji': '🎮', 'title': {'ru': 'Brawl Stars', 'en': 'Brawl Stars'}, 'items': [
        {'id': 'p_brawl_pass', 'img': 'https://raw.githubusercontent.com/HeversShop/mybot22/main/webapp/icons/brawlstars.png', 'title': {'ru': 'Brawl Pass', 'en': 'Brawl Pass'},
         'kind': 'fixed', 'price': 3.15, 'note': {'ru': '300 рублей', 'en': '300 RUB'}},
        {'id': 'p_brawl_plus_new', 'img': 'https://raw.githubusercontent.com/HeversShop/mybot22/main/webapp/icons/brawlstars.png', 'title': {'ru': 'Brawl Pass Plus', 'en': 'Brawl Pass Plus'},
         'kind': 'fixed', 'price': 3.68, 'note': {'ru': '350 рублей', 'en': '350 RUB'}},
    ]},
    {'id': 'ai', 'emoji': '🤖', 'title': {'ru': 'AI Подписки', 'en': 'AI Subscriptions'}, 'items': [
        {'id': 'p_gpt_plus_180', 'img': 'https://raw.githubusercontent.com/HeversShop/mybot22/main/webapp/icons/chatgpt.png', 'emoji': '💬', 'title': {'ru': 'ChatGPT Plus (Личный)', 'en': 'ChatGPT Plus (Personal)'},
         'kind': 'fixed', 'price': 1.89, 'note': {'ru': '180 рублей / Гарантия', 'en': '180 RUB / Warranty'}},
        {'id': 'p_gemini_18m', 'img': 'https://raw.githubusercontent.com/HeversShop/mybot22/main/webapp/icons/gemini.png', 'emoji': '✨', 'title': {'ru': 'Gemini 18 мес', 'en': 'Gemini 18m'},
         'kind': 'fixed', 'price': 1.05, 'note': {'ru': '100 рублей / Гарантия', 'en': '100 RUB / Warranty'}},
    ]},
    {'id': 'virta', 'emoji': '💰', 'title': {'ru': 'Игровая Валюта', 'en': 'Game Currency'}, 'items': [
        {'id': 'p_radmir', 'img': 'https://raw.githubusercontent.com/HeversShop/mybot22/main/webapp/icons/radmir.png', 'title': {'ru': 'Radmir Вирты', 'en': 'Radmir Virts'},
         'kind': 'perUnit', 'base': 0.55, 'unit': '1kk', 'step': 1, 'def': 25, 'min': 25,
         'note': {'ru': '52р за 1кк', 'en': '52 RUB per 1m'}},
        {'id': 'p_amazing', 'img': 'https://raw.githubusercontent.com/HeversShop/mybot22/main/webapp/icons/amazing.png', 'title': {'ru': 'Amazing Вирты', 'en': 'Amazing Virts'},
         'kind': 'perUnit', 'base': 0.47, 'unit': '1kk', 'step': 1, 'def': 25, 'min': 25,
         'note': {'ru': '45р за 1кк', 'en': '45 RUB per 1m'}},
        {'id': 'p_black_russia', 'img': 'https://raw.githubusercontent.com/HeversShop/mybot22/main/webapp/icons/blackrussia.png', 'title': {'ru': 'Black Russia Вирты', 'en': 'Black Russia Virts'},
         'kind': 'perUnit', 'base': 0.37, 'unit': '1kk', 'step': 1, 'def': 30, 'min': 30,
         'note': {'ru': '35р за 1кк', 'en': '35 RUB per 1m'}},
        {'id': 'p_majestic', 'img': 'https://raw.githubusercontent.com/HeversShop/mybot22/main/webapp/icons/majestic.png', 'title': {'ru': 'Majestic Вирты', 'en': 'Majestic Virts'},
         'kind': 'perUnit', 'base': 0.0021, 'unit': '1k', 'step': 1000, 'def': 5500, 'min': 5500,
         'note': {'ru': '0.20р за 1к', 'en': '0.20 RUB per 1k'}},
        {'id': 'p_arizona', 'img': 'https://raw.githubusercontent.com/HeversShop/mybot22/main/webapp/icons/arizona.png', 'title': {'ru': 'Arizona RP Вирты', 'en': 'Arizona RP Virts'},
         'kind': 'perUnit', 'base': 0.0026, 'unit': '1kk', 'step': 1000, 'def': 5700, 'min': 5700,
         'note': {'ru': '0.25р за 1кк', 'en': '0.25 RUB per 1m'}},
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
