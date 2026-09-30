'''Product catalog for Hevers Shop. Base prices in USD; +12% markup applied in utils.
Items with id in SKIP_MARKUP_IDS use price as-is (no extra markup in catalog).
EXCLUDED from price bump and new-product notifications: stars, brawl (Battle Pass).
'''

# Category IDs excluded from price increase and new-item notifications
EXCLUDED_CATS = {'stars', 'brawl'}

CATALOG = [
    {'id': 'stars', 'emoji': '\u2b50', 'title': {'ru': 'Telegram Stars', 'en': 'Telegram Stars'}, 'items': [
        {'id': 'p_stars_1k', 'img': 'https://img.icons8.com/color/96/telegram-app.png', 'title': {'ru': 'Telegram Stars 1000', 'en': 'Stars 1000'},
         'kind': 'per1000', 'base': 12.0, 'unit': 'Stars', 'step': 500, 'def': 1000, 'min': 1},
    ]},
    {'id': 'tiktok', 'emoji': '\U0001f4f1', 'title': {'ru': 'TikTok', 'en': 'TikTok'}, 'items': [
        {'id': 'p_tt_coins', 'img': 'https://img.icons8.com/color/96/tiktok.png', 'title': {'ru': 'TikTok \u041c\u043e\u043d\u0435\u0442\u044b', 'en': 'TikTok Coins'},
         'kind': 'perUnit', 'base': 0.013524, 'unit': '\u041c\u043e\u043d\u0435\u0442', 'step': 100, 'def': 100, 'min': 100,
         'note': {'ru': '\u0412\u0445\u043e\u0434 \u043d\u0430 \u0430\u043a\u043a\u0430\u0443\u043d\u0442. ~1.29\u0440 \u0437\u0430 1 \u0448\u0442.', 'en': 'Account login. ~1.29 RUB per pc.'}},
    ]},
    {'id': 'rbx', 'emoji': '\U0001f7e9', 'title': {'ru': 'Roblox', 'en': 'Roblox'}, 'items': [
        {'id': 'p_rbx_acc', 'img': 'https://img.icons8.com/color/96/roblox.png', 'title': {'ru': 'Robux Account', 'en': 'Robux Account'},
         'kind': 'perUnit', 'base': 0.004379, 'unit': 'R$', 'step': 1000, 'def': 1000, 'min': 1000,
         'note': {'ru': '$4.38 - 1000 R$ (\u0410\u043a\u043a\u0430\u0443\u043d\u0442). \u0412\u044b\u0434\u0430\u0447\u0430 5 \u0434\u043d\u0435\u0439.', 'en': '$4.38 - 1000 R$ (Account). 5 days delivery.'}},
        {'id': 'p_rbxgp_new', 'img': 'https://img.icons8.com/color/96/roblox.png', 'title': {'ru': 'Robux GamePass', 'en': 'Robux GP'},
         'kind': 'perUnit', 'base': 0.004637, 'unit': 'R$', 'step': 1000, 'def': 1000, 'min': 1000,
         'note': {'ru': '$4.64 - 1000 \u0440\u0431 (\u0433\u0435\u0439\u043c\u043f\u0430\u0441\u0441). \u0412\u044b\u0434\u0430\u0447\u0430 5 \u0434\u043d\u0435\u0439.', 'en': '$4.64 - 1000 rb (GP). 5 days delivery.'}},
        {'id': 'p_rbxpv_new', 'img': 'https://img.icons8.com/color/96/roblox-studio.png', 'title': {'ru': 'Robux Private Server', 'en': 'Robux Private'},
         'kind': 'perUnit', 'base': 0.003864, 'unit': 'R$', 'step': 1000, 'def': 1000, 'min': 1000,
         'note': {'ru': '$3.86 - 1000 \u0440\u0431 (\u043f\u0440\u0438\u0432\u0430\u0442\u043d\u044b\u0439 \u0441\u0435\u0440\u0432\u0435\u0440). 5 \u0434\u043d\u0435\u0439.', 'en': '$3.86 - 1000 rb (PV). 5 days delivery.'}},
    ]},
    # Brawl Stars (Battle Pass) -- EXCLUDED from price bumps and notifications
    {'id': 'brawl', 'emoji': '\U0001f3ae', 'title': {'ru': 'Brawl Stars', 'en': 'Brawl Stars'}, 'items': [
        {'id': 'p_brawl_pass', 'img': 'https://sc04.alicdn.com/kf/A7f0cb151d8bf4cbfa877468e1d106cf9t.jpg', 'title': {'ru': 'Brawl Pass', 'en': 'Brawl Pass'},
         'kind': 'fixed', 'price': 3.15, 'note': {'ru': '300\u0440. \u041a\u043e\u0434 \u0438\u043b\u0438 \u0432\u0445\u043e\u0434 \u043d\u0430 \u0430\u043a\u043a.', 'en': '300 RUB. Code or login.'}},
        {'id': 'p_brawl_plus_new', 'img': 'https://sc04.alicdn.com/kf/A7f0cb151d106cf9t.jpg', 'title': {'ru': 'Brawl Pass Plus', 'en': 'Brawl Pass Plus'},
         'kind': 'fixed', 'price': 3.68, 'note': {'ru': '350\u0440. \u041a\u043e\u0434 \u0438\u043b\u0438 \u0432\u0445\u043e\u0434 \u043d\u0430 \u0430\u043a\u043a.', 'en': '350 RUB. Code or login.'}},
    ]},
    {'id': 'ai', 'emoji': '\U0001f916', 'title': {'ru': 'AI \u041f\u043e\u0434\u043f\u0438\u0441\u043a\u0438', 'en': 'AI Subs'}, 'items': [
        {'id': 'p_gpt_p', 'title': {'ru': 'ChatGPT Plus (\u041b\u0438\u0447\u043d\u044b\u0439)', 'en': 'ChatGPT Plus'}, 'img': 'https://img.icons8.com/color/96/chatgpt.png', 'base': 2.43455, 'unit': '\u043c\u0435\u0441', 'note': {'ru': '~231\u0440. \u041b\u0438\u0447\u043d\u044b\u0439 \u0430\u043a\u043a, \u0433\u0430\u0440\u0430\u043d\u0442\u0438\u044f.', 'en': '~231 RUB. Personal, warranty.'}},
        {'id': 'p_gpt_acc', 'title': {'ru': 'ChatGPT Plus (\u0410\u043a\u043a\u0430\u0443\u043d\u0442)', 'en': 'ChatGPT Plus'}, 'img': 'https://img.icons8.com/color/96/chatgpt.png', 'base': 4.06985, 'unit': '\u043c\u0435\u0441', 'note': {'ru': '~387\u0440. \u0413\u0430\u0440\u0430\u043d\u0442\u0438\u044f \u043d\u0430 \u0432\u0435\u0441\u044c \u0441\u0440\u043e\u043a.', 'en': '~387 RUB. Full warranty.'}},
        {'id': 'p_gem_g', 'title': {'ru': 'Gemini 18\u043c (\u0413\u0430\u0440\u0430\u043d\u0442\u0438\u044f)', 'en': 'Gemini 18m'}, 'img': 'https://img.icons8.com/color/96/google-logo.png', 'base': 1.3524, 'unit': '\u0430\u043a\u043a', 'note': {'ru': '~128\u0440. \u0413\u0430\u0440\u0430\u043d\u0442\u0438\u044f \u043d\u0430 \u0432\u0435\u0441\u044c \u0441\u0440\u043e\u043a.', 'en': '~128 RUB. Full warranty.'}},
        {'id': 'p_gem_ng', 'title': {'ru': 'Gemini 18\u043c (\u0411\u0435\u0437 \u0433\u0430\u0440.)', 'en': 'Gemini 18m'}, 'img': 'https://img.icons8.com/color/96/google-logo.png', 'base': 0.47656, 'unit': '\u0430\u043a\u043a', 'note': {'ru': '~45\u0440. \u0411\u0435\u0437 \u0433\u0430\u0440\u0430\u043d\u0442\u0438\u0438.', 'en': '~45 RUB. No warranty.'}},
        {'id': 'p_grok_g', 'title': {'ru': 'Super Grok (\u0413\u0430\u0440\u0430\u043d\u0442\u0438\u044f)', 'en': 'Super Grok'}, 'img': 'https://img.icons8.com/color/96/x.png', 'base': 4.06985, 'unit': '\u043c\u0435\u0441', 'note': {'ru': '~387\u0440. \u0413\u0430\u0440\u0430\u043d\u0442\u0438\u044f \u043d\u0430 \u0432\u0435\u0441\u044c \u0441\u0440\u043e\u043a.', 'en': '~387 RUB. Full warranty.'}},
        {'id': 'p_grok_ng', 'title': {'ru': 'Super Grok (\u0411\u0435\u0437 \u0433\u0430\u0440.)', 'en': 'Super Grok'}, 'img': 'https://img.icons8.com/color/96/x.png', 'base': 2.71745, 'unit': '\u043c\u0435\u0441', 'note': {'ru': '~258\u0440. \u0411\u0435\u0437 \u0433\u0430\u0440\u0430\u043d\u0442\u0438\u0438.', 'en': '~258 RUB. No warranty.'}},
        {'id': 'p_cld_30_ng', 'title': {'ru': 'Claude PRO 30\u0434 (\u0411\u0435\u0437 \u0433\u0430\u0440.)', 'en': 'Claude PRO 30d'}, 'img': 'https://img.icons8.com/color/96/brain.png', 'base': 4.06985, 'unit': '\u043c\u0435\u0441', 'note': {'ru': '~387\u0440. \u0411\u0435\u0437 \u0433\u0430\u0440\u0430\u043d\u0442\u0438\u0438.', 'en': '~387 RUB. No warranty.'}},
        {'id': 'p_cld_365_ng', 'title': {'ru': 'Claude PRO 365\u0434 (\u0411\u0435\u0437 \u0433\u0430\u0440.)', 'en': 'Claude PRO 365d'}, 'img': 'https://img.icons8.com/color/96/brain.png', 'base': 20.33775, 'unit': '\u0433\u043e\u0434', 'note': {'ru': '~1932\u0440. \u0411\u0435\u0437 \u0433\u0430\u0440\u0430\u043d\u0442\u0438\u0438.', 'en': '~1932 RUB. No warranty.'}},
        {'id': 'p_cld_30_g', 'title': {'ru': 'Claude PRO 30\u0434 (\u0413\u0430\u0440\u0430\u043d\u0442\u0438\u044f)', 'en': 'Claude PRO 30d'}, 'img': 'https://img.icons8.com/color/96/brain.png', 'base': 13.5631, 'unit': '\u043c\u0435\u0441', 'note': {'ru': '~1288\u0440. \u0421\u043f\u043e\u0441\u043e\u0431, \u0441 \u0433\u0430\u0440\u0430\u043d\u0442\u0438\u0435\u0439.', 'en': '~1288 RUB. Method, warranty.'}},
    ]},
     {'id': 'standoff', 'emoji': '\U0001f52b', 'title': {'ru': 'Standoff 2', 'en': 'Standoff 2'}, 'items': [
         {'id': 'p_so2_gold_100', 'img': 'https://img.icons8.com/color/96/gold-bars.png',
          'title': {'ru': 'Standoff 2 \u0413\u043e\u043b\u0434\u0430 100', 'en': 'Standoff 2 Gold 100'},
          'kind': 'fixed', 'price': 0.386,
          'note': {'ru': '~37\u0440. \u041f\u043e\u043f\u043e\u043b\u043d\u0435\u043d\u0438\u0435 \u043d\u0430 \u0430\u043a\u043a\u0430\u0443\u043d\u0442.', 'en': '~37 RUB. Top-up to account.'}},
         {'id': 'p_so2_gold_500', 'img': 'https://img.icons8.com/color/96/gold-bars.png',
          'title': {'ru': 'Standoff 2 \u0413\u043e\u043b\u0434\u0430 500', 'en': 'Standoff 2 Gold 500'},
          'kind': 'fixed', 'price': 1.8216,
          'note': {'ru': '~173\u0440. \u041f\u043e\u043f\u043e\u043b\u043d\u0435\u043d\u0438\u0435 \u043d\u0430 \u0430\u043a\u043a\u0430\u0443\u043d\u0442.', 'en': '~173 RUB. Top-up to account.'}},
         {'id': 'p_so2_gold_1000', 'img': 'https://img.icons8.com/color/96/gold-bars.png',
          'title': {'ru': 'Standoff 2 \u0413\u043e\u043b\u0434\u0430 1000', 'en': 'Standoff 2 Gold 1000'},
          'kind': 'fixed', 'price': 3.4017,
          'note': {'ru': '~323\u0440. \u041f\u043e\u043f\u043e\u043b\u043d\u0435\u043d\u0438\u0435 \u043d\u0430 \u0430\u043a\u043a\u0430\u0443\u043d\u0442.', 'en': '~323 RUB. Top-up to account.'}},
         {'id': 'p_so2_gold_2000', 'img': 'https://img.icons8.com/color/96/gold-bars.png',
          'title': {'ru': 'Standoff 2 \u0413\u043e\u043b\u0434\u0430 2000', 'en': 'Standoff 2 Gold 2000'},
          'kind': 'fixed', 'price': 6.3756,
          'note': {'ru': '~606\u0440. \u041f\u043e\u043f\u043e\u043b\u043d\u0435\u043d\u0438\u0435 \u043d\u0430 \u0430\u043a\u043a\u0430\u0443\u043d\u0442.', 'en': '~606 RUB. Top-up to account.'}},
     ]},
    {'id': 'virta', 'emoji': '\U0001f4b0', 'title': {'ru': '\u0412\u0438\u0440\u0442\u044b', 'en': 'Virts'}, 'items': [
        {'id': 'p_rad', 'img': 'https://sc04.alicdn.com/kf/A9212c3b0f6d44b9c90de0a8d54f2ad4cx.jpg', 'title': {'ru': 'Radmir RP', 'en': 'Radmir'},
         'kind': 'perUnit', 'base': 0.7084, 'unit': '1kk', 'step': 1, 'def': 25, 'min': 25,
         'note': {'ru': '~67\u0440/1\u043a\u043a. \u0411\u0430\u043d\u043a, \u0442\u0440\u0435\u0439\u0434, \u0430\u0432\u0442\u043e.', 'en': '~67r/1m. Delivery: Bank/Trade.'}},
        {'id': 'p_ama', 'img': 'https://sc04.alicdn.com/kf/A73993f3356a7447187b73f4b8b4fea8dP.jpg', 'title': {'ru': 'Amazing RP', 'en': 'Amazing'},
         'kind': 'perUnit', 'base': 0.60536, 'unit': '1kk', 'step': 1, 'def': 25, 'min': 25,
         'note': {'ru': '~58\u0440/1\u043a\u043a. \u0411\u0430\u043d\u043a, \u0442\u0440\u0435\u0439\u0434, \u0430\u0432\u0442\u043e.', 'en': '~58r/1m. Delivery: Bank/Trade.'}},
        {'id': 'p_br', 'img': 'https://sc04.alicdn.com/kf/A0e637ec6d6f141e39e483a5fc88d325bH.jpg', 'title': {'ru': 'Black Russia', 'en': 'Black Russia'},
         'kind': 'perUnit', 'base': 0.47656, 'unit': '1kk', 'step': 1, 'def': 30, 'min': 30,
         'note': {'ru': '~45\u0440/1\u043a\u043a. \u0411\u0430\u043d\u043a, \u0442\u0440\u0435\u0439\u0434, \u0430\u0432\u0442\u043e.', 'en': '~45r/1m. Delivery: Bank/Trade.'}},
        {'id': 'p_maj', 'img': 'https://sc04.alicdn.com/kf/A6fab1941243d4afaa1f1641cd9e3f6cfk.jpg', 'title': {'ru': 'Majestic RP', 'en': 'Majestic'},
         'kind': 'perUnit', 'base': 4.06985, 'unit': '1kk', 'step': 1, 'def': 25, 'min': 25,
         'note': {'ru': '\u041f\u043e\u043a\u0435\u0440, \u0431\u0430\u043d\u043a, \u0430\u0432\u0442\u043e.', 'en': 'Delivery: Poker/Bank.'}},
        {'id': 'p_arz', 'img': 'https://sc04.alicdn.com/kf/A356ac4bfea8f4fbe902d356556a27f210.jpg', 'title': {'ru': 'Arizona RP', 'en': 'Arizona'},
         'kind': 'perUnit', 'base': 3.38744, 'unit': '1kkk', 'step': 1, 'def': 1, 'min': 1,
         'note': {'ru': '\u0411\u0430\u043d\u043a, \u0442\u0440\u0435\u0439\u0434, \u0430\u0432\u0442\u043e.', 'en': 'Delivery: Bank/Trade.'}},
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


def products_for_notifications():
    """Return items from categories NOT in EXCLUDED_CATS."""
    out = []
    for cat in CATALOG:
        if cat['id'] in EXCLUDED_CATS:
            continue
        for p in cat.get('items', []):
            out.append({'cat': cat, 'product': p})
    return out
