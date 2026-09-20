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
        {'id': 'p_rad', 'img': 'https://sc04.alicdn.com/kf/A9212c3b0f6d44b9c90de0a8d54f2ad4cx.jpg', 'title': {'ru': 'Radmir RP', 'en': 'Radmir'},
         'kind': 'perUnit', 'base': 0.55, 'unit': '1kk', 'step': 1, 'def': 25, 'min': 25,
         'note': {'ru': '52р/1кк. Банк, трейд, авто.', 'en': '52r/1m. Delivery: Bank/Trade.'}},
        {'id': 'p_ama', 'img': 'https://sc04.alicdn.com/kf/A73993f3356a7447187b73f4b8b4fea8dP.jpg', 'title': {'ru': 'Amazing RP', 'en': 'Amazing'},
         'kind': 'perUnit', 'base': 0.47, 'unit': '1kk', 'step': 1, 'def': 25, 'min': 25,
         'note': {'ru': '45р/1кк. Банк, трейд, авто.', 'en': '45r/1m. Delivery: Bank/Trade.'}},
        {'id': 'p_br', 'img': 'https://sc04.alicdn.com/kf/A0e637ec6d6f141e39e483a5fc88d325bH.jpg', 'title': {'ru': 'Black Russia', 'en': 'Black Russia'},
         'kind': 'perUnit', 'base': 0.37, 'unit': '1kk', 'step': 1, 'def': 30, 'min': 30,
         'note': {'ru': '35р/1кк. Банк, трейд, авто.', 'en': '35r/1m. Delivery: Bank/Trade.'}},
        {'id': 'p_maj', 'img': 'https://sc04.alicdn.com/kf/A6fab1941243d4afaa1f1641cd9e3f6cfk.jpg', 'title': {'ru': 'Majestic RP', 'en': 'Majestic'},
         'kind': 'perUnit', 'base': 3.16, 'unit': '1kk', 'step': 1, 'def': 25, 'min': 25,
         'note': {'ru': '0.30р/1к. Покер, банк, авто.', 'en': '0.30r/1k. Delivery: Poker/Bank.'}},
        {'id': 'p_arz', 'img': 'https://sc04.alicdn.com/kf/A356ac4bfea8f4fbe902d356556a27f210.jpg', 'title': {'ru': 'Arizona RP', 'en': 'Arizona'},
         'kind': 'perUnit', 'base': 2.63, 'unit': '1kkk', 'step': 1, 'def': 1, 'min': 1,
         'note': {'ru': '0.25р/1кк. Банк, трейд, авто.', 'en': '0.25r/1m. Delivery: Bank/Trade.'}},
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
