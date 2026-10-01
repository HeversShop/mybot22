'''Product catalog for Hevers Shop. Base prices in USD; +12% markup applied in utils.
Items with id in SKIP_MARKUP_IDS use price as-is (no extra markup in catalog).
Only the Standoff 2 Gold line is kept in the catalog.
'''

# Category IDs excluded from price increase and new-item notifications
EXCLUDED_CATS = set()

CATALOG = [
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
