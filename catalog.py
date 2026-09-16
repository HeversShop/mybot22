'''Product catalog for Hevers Shop. Base prices in USD; +12% markup applied in utils.'''

CATALOG = [
    {'id': 'stars', 'emoji': '⭐', 'title': {'ru': 'Telegram Stars', 'en': 'Telegram Stars'}, 'items': [
        {'id': 'p_stars_1k', 'emoji': '⭐', 'title': {'ru': 'Telegram Stars', 'en': 'Telegram Stars'},
         'kind': 'per1000', 'base': 12.0, 'unit': 'Stars', 'step': 500, 'def': 1000, 'min': 1},
    ]},
    {'id': 'brawl', 'emoji': '🎮', 'title': {'ru': 'Brawl Stars', 'en': 'Brawl Stars'}, 'items': [
        {'id': 'p_brawl', 'emoji': '🎟️', 'title': {'ru': 'Brawl Pass', 'en': 'Brawl Pass'}, 'kind': 'fixed', 'base': 3.31},
        {'id': 'p_brawl_plus', 'emoji': '🎟️', 'title': {'ru': 'Brawl Pass Plus', 'en': 'Brawl Pass Plus'}, 'kind': 'fixed', 'base': 3.96},
    ]},
    {'id': 'ai', 'emoji': '✨', 'title': {'ru': 'AI подписки', 'en': 'AI subscriptions'}, 'items': [
        {'id': 'p_gem_18m', 'emoji': '✨', 'title': {'ru': 'Gemini · 18 мес.', 'en': 'Gemini · 18m'}, 'kind': 'fixed', 'base': 0.47},
        {'id': 'p_gem_plus', 'emoji': '✨', 'title': {'ru': 'Google AI Plus', 'en': 'Google AI Plus'}, 'kind': 'fixed', 'base': 5.28},
        {'id': 'p_gem_pro', 'emoji': '✨', 'title': {'ru': 'Google AI Pro', 'en': 'Google AI Pro'}, 'kind': 'fixed', 'base': 10.56},
        {'id': 'p_gpt_nw', 'emoji': '💬', 'title': {'ru': 'ChatGPT NW', 'en': 'ChatGPT NW'}, 'kind': 'fixed', 'base': 1.28, 'note': {'ru': 'Опт от 50 usd дешевле', 'en': 'Bulk from 50 usd cheaper'}},
        {'id': 'p_gpt_fw', 'emoji': '💬', 'title': {'ru': 'ChatGPT FW', 'en': 'ChatGPT FW'}, 'kind': 'fixed', 'base': 1.71, 'note': {'ru': 'Опт от 50 usd дешевле', 'en': 'Bulk from 50 usd cheaper'}},
        {'id': 'p_gpt_plus', 'emoji': '💬', 'title': {'ru': 'ChatGPT Plus', 'en': 'ChatGPT Plus'}, 'kind': 'fixed', 'base': 10.56},
        {'id': 'p_cld_1m', 'emoji': '🧠', 'title': {'ru': 'Claude 1M', 'en': 'Claude 1M'}, 'kind': 'fixed', 'base': 9.51},
        {'id': 'p_cld_pro', 'emoji': '🧠', 'title': {'ru': 'Claude Pro', 'en': 'Claude Pro'}, 'kind': 'fixed', 'base': 10.56},
        {'id': 'p_cld_team', 'emoji': '🧠', 'title': {'ru': 'Claude Team', 'en': 'Claude Team'}, 'kind': 'fixed', 'base': 24.29},
        {'id': 'p_cld_max5', 'emoji': '🧠', 'title': {'ru': 'Claude MAX 5x', 'en': 'Claude MAX 5x'}, 'kind': 'fixed', 'base': 51.75},
        {'id': 'p_cld_max20', 'emoji': '🧠', 'title': {'ru': 'Claude MAX 20x', 'en': 'Claude MAX 20x'}, 'kind': 'fixed', 'base': 83.43},
        {'id': 'p_grok_year', 'emoji': '✖️', 'title': {'ru': 'Grok · 1 год', 'en': 'Grok · 1y'}, 'kind': 'fixed', 'base': 10.71},
        {'id': 'p_grok_3m', 'emoji': '✖️', 'title': {'ru': 'GROK · 3 мес.', 'en': 'GROK · 3m'}, 'kind': 'fixed', 'base': 3.70},
        {'id': 'p_grok_prem3m', 'emoji': '✖️', 'title': {'ru': 'X Premium + Grok · 3 мес.', 'en': 'X Premium + Grok · 3m'}, 'kind': 'fixed', 'base': 3.70},
        {'id': 'p_grok_1m', 'emoji': '✖️', 'title': {'ru': 'Grok · 1 мес.', 'en': 'Grok · 1m'}, 'kind': 'fixed', 'base': 1.06},
        {'id': 'p_grok_1w', 'emoji': '✖️', 'title': {'ru': 'Grok · 1 нед.', 'en': 'Grok · 1w'}, 'kind': 'fixed', 'base': 0.43},
    ]},
    {'id': 'rbxacc', 'emoji': '🟩', 'title': {'ru': 'Robux аккаунтом', 'en': 'Robux via account'}, 'items': [
        {'id': 'p_rbxacc', 'emoji': '🟩', 'title': {'ru': 'Robux аккаунтом', 'en': 'Robux via account'},
         'kind': 'per1000', 'base': 4.23, 'unit': 'R$', 'step': 1000, 'def': 3000, 'min': 12.5,
         'tier_units': 45000, 'tier_rate': 3.81,
         'note': {'ru': 'Выдаётся вручную тех. поддержкой @heverssupport', 'en': 'Delivered manually by support @heverssupport'}},
    ]},
    {'id': 'rbxgp', 'emoji': '🟦', 'title': {'ru': 'Robux GamePass', 'en': 'Robux GamePass'}, 'items': [
        {'id': 'p_rbxgp', 'emoji': '🟦', 'title': {'ru': 'Robux GamePass', 'en': 'Robux GamePass'},
         'kind': 'per1000', 'base': 4.44, 'unit': 'R$', 'step': 1000, 'def': 3000, 'min': 12.5,
         'tier_units': 45000, 'tier_rate': 3.91,
         'note': {'ru': 'Выдача через Game Pass - пришлите ссылку на ваш пасс', 'en': 'Delivered via Game Pass - send your pass link'}},
    ]},
    {'id': 'rbxgrp', 'emoji': '🟪', 'title': {'ru': 'Robux группой', 'en': 'Robux via group'}, 'items': [
        {'id': 'p_rbxgrp', 'emoji': '🟪', 'title': {'ru': 'Robux группой', 'en': 'Robux via group'},
         'kind': 'per1000', 'base': 4.12, 'unit': 'R$', 'step': 1000, 'def': 3000, 'min': 7,
         'tier_units': 45000, 'tier_rate': 4.02,
         'note': {'ru': 'Выдача через группу Roblox (холд Roblox ~14 дней)', 'en': 'Delivered via Roblox group (~14-day hold)'}},
    ]},
    {'id': 'rbxgc', 'emoji': '🎁', 'title': {'ru': 'Roblox Gift Cards', 'en': 'Roblox Gift Cards'}, 'items': [
        {'id': 'p_rbxgc_10', 'emoji': '🎁', 'title': {'ru': 'Roblox Gift Card $10', 'en': 'Roblox Gift Card $10'}, 'kind': 'fixed', 'price': 7.00, 'face': 10, 'note': {'ru': 'На 30% ниже официального. Код выдаёт поддержка после оплаты', 'en': '30% below official. Code delivered by support after payment'}},
        {'id': 'p_rbxgc_25', 'emoji': '🎁', 'title': {'ru': 'Roblox Gift Card $25', 'en': 'Roblox Gift Card $25'}, 'kind': 'fixed', 'price': 16.50, 'face': 25, 'note': {'ru': 'На 34% ниже официального. Код выдаёт поддержка после оплаты', 'en': '34% below official. Code delivered by support after payment'}},
        {'id': 'p_rbxgc_50', 'emoji': '🎁', 'title': {'ru': 'Roblox Gift Card $50', 'en': 'Roblox Gift Card $50'}, 'kind': 'fixed', 'price': 31.50, 'face': 50, 'note': {'ru': 'На 37% ниже официального. Код выдаёт поддержка после оплаты', 'en': '37% below official. Code delivered by support after payment'}},
        {'id': 'p_rbxgc_100', 'emoji': '🎁', 'title': {'ru': 'Roblox Gift Card $100', 'en': 'Roblox Gift Card $100'}, 'kind': 'fixed', 'price': 60.00, 'face': 100, 'note': {'ru': 'На 40% ниже официального. Код выдаёт поддержка после оплаты', 'en': '40% below official. Code delivered by support after payment'}},
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
