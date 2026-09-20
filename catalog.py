'''Product catalog for Hevers Shop. Base prices in USD; +12% markup applied in utils.'''

CATALOG = [
    {'id': 'stars', 'emoji': '⭐', 'title': {'ru': 'Telegram Stars', 'en': 'Telegram Stars'}, 'items': [
        {'id': 'p_stars_1k', 'img': 'https://img.icons8.com/color/96/telegram-app.png', 'title': {'ru': 'Telegram Stars 1000', 'en': 'Stars 1000'},
         'kind': 'per1000', 'base': 12.0, 'unit': 'Stars', 'step': 500, 'def': 1000, 'min': 1},
    ]},
    {'id': 'tiktok', 'emoji': '📱', 'title': {'ru': 'TikTok', 'en': 'TikTok'}, 'items': [
        {'id': 'p_tt_coins', 'img': 'https://img.icons8.com/color/96/tiktok.png', 'title': {'ru': 'TikTok Монеты', 'en': 'TikTok Coins'},
         'kind': 'perUnit', 'base': 0.0105, 'unit': 'Монет', 'step': 100, 'def': 100, 'min': 100,
         'note': {'ru': 'Вход на аккаунт. 1.05р за 1 шт.', 'en': 'Account login. 1.05 RUB per pc.'}},
    ]},
    {'id': 'rbx', 'emoji': '🟩', 'title': {'ru': 'Roblox', 'en': 'Roblox'}, 'items': [
        {'id': 'p_rbxgp_new', 'img': 'https://img.icons8.com/color/96/roblox.png', 'title': {'ru': 'Robux GamePass', 'en': 'Robux GP'},
         'kind': 'perUnit', 'base': 0.0036, 'unit': 'R$', 'step': 1000, 'def': 1000, 'min': 1000,
         'note': {'ru': '$3.6 - 1000 рб (геймпасс). Выдача 5 дней.', 'en': '$3.6 - 1000 rb (GP). 5 days delivery.'}},
        {'id': 'p_rbxpv_new', 'img': 'https://img.icons8.com/color/96/roblox-studio.png', 'title': {'ru': 'Robux Private Server', 'en': 'Robux Private'},
         'kind': 'perUnit', 'base': 0.003, 'unit': 'R$', 'step': 1000, 'def': 1000, 'min': 1000,
         'note': {'ru': '$3 - 1000 рб (приватный сервер). 5 дней.', 'en': '$3 - 1000 rb (PV). 5 days delivery.'}},
    ]},
    {'id': 'brawl', 'emoji': '🎮', 'title': {'ru': 'Brawl Stars', 'en': 'Brawl Stars'}, 'items': [
        {'id': 'p_brawl_pass', 'img': 'https://sc04.alicdn.com/kf/A7f0cb151d8bf4cbfa877468e1d106cf9t.jpg', 'title': {'ru': 'Brawl Pass', 'en': 'Brawl Pass'},
         'kind': 'fixed', 'price': 3.15, 'note': {'ru': '300р. Код или вход на акк.', 'en': '300 RUB. Code or login.'}},
        {'id': 'p_brawl_plus_new', 'img': 'https://sc04.alicdn.com/kf/A7f0cb151d106cf9t.jpg', 'title': {'ru': 'Brawl Pass Plus', 'en': 'Brawl Pass Plus'},
         'kind': 'fixed', 'price': 3.68, 'note': {'ru': '350р. Код или вход на акк.', 'en': '350 RUB. Code or login.'}},
    ]},
    {'id': 'ai', 'emoji': '🤖', 'title': {'ru': 'AI Подписки', 'en': 'AI Subs'}, 'items': [
        {'id': 'p_gpt_p', 'title': {'ru': 'ChatGPT Plus (Личный)', 'en': 'ChatGPT Plus'}, 'img': 'https://img.icons8.com/color/96/chatgpt.png', 'base': 1.89, 'unit': 'мес', 'note': {'ru': '180р. Личный акк, гарантия.', 'en': '180 RUB. Personal, warranty.'}},
        {'id': 'p_gpt_acc', 'title': {'ru': 'ChatGPT Plus (Аккаунт)', 'en': 'ChatGPT Plus'}, 'img': 'https://img.icons8.com/color/96/chatgpt.png', 'base': 3.16, 'unit': 'мес', 'note': {'ru': '300р. Гарантия на весь срок.', 'en': '300 RUB. Full warranty.'}},
        {'id': 'p_gem_g', 'title': {'ru': 'Gemini 18м (Гарантия)', 'en': 'Gemini 18m'}, 'img': 'https://img.icons8.com/color/96/google-logo.png', 'base': 1.05, 'unit': 'акк', 'note': {'ru': '100р. Гарантия на весь срок.', 'en': '100 RUB. Full warranty.'}},
        {'id': 'p_gem_ng', 'title': {'ru': 'Gemini 18м (Без гар.)', 'en': 'Gemini 18m'}, 'img': 'https://img.icons8.com/color/96/google-logo.png', 'base': 0.37, 'unit': 'акк', 'note': {'ru': '35р. Без гарантии.', 'en': '35 RUB. No warranty.'}},
        {'id': 'p_grok_g', 'title': {'ru': 'Super Grok (Гарантия)', 'en': 'Super Grok'}, 'img': 'https://img.icons8.com/color/96/x.png', 'base': 3.16, 'unit': 'мес', 'note': {'ru': '300р. Гарантия на весь срок.', 'en': '300 RUB. Full warranty.'}},
        {'id': 'p_grok_ng', 'title': {'ru': 'Super Grok (Без гар.)', 'en': 'Super Grok'}, 'img': 'https://img.icons8.com/color/96/x.png', 'base': 2.11, 'unit': 'мес', 'note': {'ru': '200р. Без гарантии.', 'en': '200 RUB. No warranty.'}},
        {'id': 'p_cld_30_ng', 'title': {'ru': 'Claude PRO 30д (Без гар.)', 'en': 'Claude PRO 30d'}, 'img': 'https://img.icons8.com/color/96/brain.png', 'base': 3.16, 'unit': 'мес', 'note': {'ru': '300р. Без гарантии.', 'en': '300 RUB. No warranty.'}},
        {'id': 'p_cld_365_ng', 'title': {'ru': 'Claude PRO 365д (Без гар.)', 'en': 'Claude PRO 365d'}, 'img': 'https://img.icons8.com/color/96/brain.png', 'base': 15.79, 'unit': 'год', 'note': {'ru': '1500р. Без гарантии.', 'en': '1500 RUB. No warranty.'}},
        {'id': 'p_cld_30_g', 'title': {'ru': 'Claude PRO 30д (Гарантия)', 'en': 'Claude PRO 30d'}, 'img': 'https://img.icons8.com/color/96/brain.png', 'base': 10.53, 'unit': 'мес', 'note': {'ru': '1000р. Способ, с гарантией.', 'en': '1000 RUB. Method, warranty.'}},
    ]},
    {'id': 'virta', 'emoji': '💰', 'title': {'ru': 'Вирты', 'en': 'Virts'}, 'items': [
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
         'note': {'ru': '0.20р/1к. Покер, банк, авто.', 'en': '0.30r/1k. Delivery: Poker/Bank.'}},
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
