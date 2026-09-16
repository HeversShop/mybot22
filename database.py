'''Async SQLite storage for users, orders and leads.'''
import aiosqlite
import os
from datetime import datetime, timezone
from config import DB_PATH

def _resolve_db_path(path):
    '''Make the DB path usable on any host.

    Creates the parent directory if needed; if it cannot be created or is not
    writable (e.g. DB_PATH=/data/... without a mounted volume), falls back to a
    local file so the bot keeps working instead of crashing.'''
    try:
        d = os.path.dirname(path)
        if d:
            os.makedirs(d, exist_ok=True)
        target = d or '.'
        if os.access(target, os.W_OK):
            return path
    except Exception:
        pass
    return 'oncedshop.db'

DB_PATH = _resolve_db_path(DB_PATH)


CREATE_USERS = '''
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    full_name TEXT,
    language TEXT DEFAULT 'ru',
    phone TEXT,
    balance REAL DEFAULT 0,
    discount REAL DEFAULT 0,
    created_at TEXT
)
'''

CREATE_ORDERS = '''
CREATE TABLE IF NOT EXISTS orders (
    order_id TEXT PRIMARY KEY,
    user_id INTEGER,
    product_id TEXT,
    title TEXT,
    quantity INTEGER,
    amount_usd REAL,
    account TEXT,
    details TEXT,
    payment_method TEXT,
    pay_amount TEXT,
    status TEXT DEFAULT 'created',
    created_at TEXT
)
'''

CREATE_LEADS = '''
CREATE TABLE IF NOT EXISTS leads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source TEXT,
    chat TEXT,
    message_id INTEGER,
    author TEXT,
    author_id INTEGER,
    text TEXT,
    matched TEXT,
    triggers TEXT,
    link TEXT,
    status TEXT DEFAULT 'new',
    created_at TEXT,
    UNIQUE(source, message_id)
)
'''


CREATE_TICKETS = '''
CREATE TABLE IF NOT EXISTS tickets (
    user_id INTEGER PRIMARY KEY,
    status TEXT DEFAULT 'open',
    unread INTEGER DEFAULT 0,
    last_text TEXT,
    last_from TEXT,
    created_at TEXT,
    updated_at TEXT
)
'''

CREATE_SUPPORT_MESSAGES = '''
CREATE TABLE IF NOT EXISTS support_messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    direction TEXT,
    admin_id INTEGER,
    text TEXT,
    created_at TEXT
)
'''

CREATE_SUPPORT_MAP = '''
CREATE TABLE IF NOT EXISTS support_map (
    chat_id INTEGER,
    message_id INTEGER,
    user_id INTEGER,
    PRIMARY KEY (chat_id, message_id)
)
'''


def _now():
    return datetime.now(timezone.utc).isoformat()


async def init_db():
    async with aiosqlite.connect(DB_PATH) as conn:
        await conn.execute(CREATE_USERS)
        await conn.execute(CREATE_ORDERS)
        await conn.execute(CREATE_LEADS)
        await conn.execute(CREATE_TICKETS)
        await conn.execute(CREATE_SUPPORT_MESSAGES)
        await conn.execute(CREATE_SUPPORT_MAP)
        await conn.execute('CREATE INDEX IF NOT EXISTS idx_support_msgs_user ON support_messages(user_id, id)')
        await conn.execute('CREATE INDEX IF NOT EXISTS idx_orders_user ON orders(user_id, created_at)')
        for ddl in (
            'ALTER TABLE users ADD COLUMN balance REAL DEFAULT 0',
            'ALTER TABLE users ADD COLUMN discount REAL DEFAULT 0',
        ):
            try:
                await conn.execute(ddl)
            except Exception:
                pass
        await conn.commit()


async def upsert_user(user_id, username, full_name, language='ru'):
    async with aiosqlite.connect(DB_PATH) as conn:
        await conn.execute(
            'INSERT INTO users (user_id, username, full_name, language, created_at) '
            'VALUES (?, ?, ?, ?, ?) '
            'ON CONFLICT(user_id) DO UPDATE SET username=excluded.username, full_name=excluded.full_name',
            (user_id, username, full_name, language, _now()),
        )
        await conn.commit()


async def set_language(user_id, language):
    async with aiosqlite.connect(DB_PATH) as conn:
        await conn.execute('UPDATE users SET language=? WHERE user_id=?', (language, user_id))
        await conn.commit()


async def get_language(user_id):
    async with aiosqlite.connect(DB_PATH) as conn:
        async with conn.execute('SELECT language FROM users WHERE user_id=?', (user_id,)) as cur:
            row = await cur.fetchone()
            return row[0] if row and row[0] else 'ru'


async def save_phone(user_id, phone):
    async with aiosqlite.connect(DB_PATH) as conn:
        await conn.execute('UPDATE users SET phone=? WHERE user_id=?', (phone, user_id))
        await conn.commit()


async def create_order(order):
    async with aiosqlite.connect(DB_PATH) as conn:
        await conn.execute(
            'INSERT INTO orders (order_id, user_id, product_id, title, quantity, amount_usd, '
            'account, details, payment_method, pay_amount, status, created_at) '
            'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
            (
                order['order_id'], order['user_id'], order.get('product_id', ''),
                order.get('title', ''), order.get('quantity', 0), order.get('amount_usd', 0.0),
                order.get('account', ''), order.get('details', ''), order.get('payment_method', ''),
                order.get('pay_amount', ''), order.get('status', 'created'), _now(),
            ),
        )
        await conn.commit()


async def set_order_status(order_id, status):
    async with aiosqlite.connect(DB_PATH) as conn:
        await conn.execute('UPDATE orders SET status=? WHERE order_id=?', (status, order_id))
        await conn.commit()


async def set_order_payment(order_id, method, pay_amount):
    async with aiosqlite.connect(DB_PATH) as conn:
        await conn.execute('UPDATE orders SET payment_method=?, pay_amount=? WHERE order_id=?',
                           (method, pay_amount, order_id))
        await conn.commit()


async def get_user_orders(user_id, limit=10):
    async with aiosqlite.connect(DB_PATH) as conn:
        async with conn.execute(
            'SELECT order_id, title, quantity, amount_usd, status, created_at '
            'FROM orders WHERE user_id=? ORDER BY created_at DESC LIMIT ?',
            (user_id, limit),
        ) as cur:
            return await cur.fetchall()


async def get_order(order_id):
    '''Return a single order as a dict, or None.'''
    async with aiosqlite.connect(DB_PATH) as conn:
        conn.row_factory = aiosqlite.Row
        async with conn.execute(
            'SELECT * FROM orders WHERE order_id=?', (order_id,),
        ) as cur:
            row = await cur.fetchone()
            return dict(row) if row else None


async def get_orders(limit=6, offset=0, status=None):
    '''Recent orders for the admin panel (newest first).'''
    async with aiosqlite.connect(DB_PATH) as conn:
        conn.row_factory = aiosqlite.Row
        if status:
            q = ('SELECT * FROM orders WHERE status=? '
                 'ORDER BY created_at DESC LIMIT ? OFFSET ?')
            p = (status, limit, offset)
        else:
            q = 'SELECT * FROM orders ORDER BY created_at DESC LIMIT ? OFFSET ?'
            p = (limit, offset)
        async with conn.execute(q, p) as cur:
            return [dict(r) for r in await cur.fetchall()]


async def count_orders(status=None):
    async with aiosqlite.connect(DB_PATH) as conn:
        if status:
            q = 'SELECT COUNT(*) FROM orders WHERE status=?'
            p = (status,)
        else:
            q = 'SELECT COUNT(*) FROM orders'
            p = ()
        async with conn.execute(q, p) as cur:
            row = await cur.fetchone()
            return row[0] if row else 0


# ---------------- Leads (chat monitor) ----------------
async def add_lead(lead):
    async with aiosqlite.connect(DB_PATH) as conn:
        cur = await conn.execute(
            'INSERT OR IGNORE INTO leads (source, chat, message_id, author, author_id, '
            'text, matched, triggers, link, status, created_at) '
            'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
            (
                lead.get('source', ''), lead.get('chat', ''), lead.get('message_id'),
                lead.get('author', ''), lead.get('author_id'), lead.get('text', ''),
                lead.get('matched', ''), lead.get('triggers', ''), lead.get('link', ''),
                lead.get('status', 'new'), _now(),
            ),
        )
        await conn.commit()
        return cur.rowcount > 0


async def count_leads(status=None):
    async with aiosqlite.connect(DB_PATH) as conn:
        if status:
            q, p = 'SELECT COUNT(*) FROM leads WHERE status=?', (status,)
        else:
            q, p = 'SELECT COUNT(*) FROM leads', ()
        async with conn.execute(q, p) as cur:
            row = await cur.fetchone()
            return row[0] if row else 0


async def get_leads(limit=5, offset=0, status=None):
    async with aiosqlite.connect(DB_PATH) as conn:
        if status:
            q = ('SELECT id, source, chat, message_id, author, author_id, text, matched, '
                 'triggers, link, status, created_at FROM leads WHERE status=? '
                 'ORDER BY id DESC LIMIT ? OFFSET ?')
            p = (status, limit, offset)
        else:
            q = ('SELECT id, source, chat, message_id, author, author_id, text, matched, '
                 'triggers, link, status, created_at FROM leads '
                 'ORDER BY id DESC LIMIT ? OFFSET ?')
            p = (limit, offset)
        async with conn.execute(q, p) as cur:
            return await cur.fetchall()


async def set_lead_status(lead_id, status):
    async with aiosqlite.connect(DB_PATH) as conn:
        await conn.execute('UPDATE leads SET status=? WHERE id=?', (status, lead_id))
        await conn.commit()


# ---------------- Balance, discount & users (admin) ----------------
async def get_user(user_id):
    async with aiosqlite.connect(DB_PATH) as conn:
        conn.row_factory = aiosqlite.Row
        async with conn.execute('SELECT * FROM users WHERE user_id=?', (user_id,)) as cur:
            row = await cur.fetchone()
            return dict(row) if row else None


async def get_balance(user_id):
    async with aiosqlite.connect(DB_PATH) as conn:
        async with conn.execute('SELECT balance FROM users WHERE user_id=?', (user_id,)) as cur:
            row = await cur.fetchone()
            return float(row[0]) if row and row[0] is not None else 0.0


async def add_balance(user_id, amount):
    async with aiosqlite.connect(DB_PATH) as conn:
        await conn.execute(
            'INSERT INTO users (user_id, balance, created_at) VALUES (?, ?, ?) '
            'ON CONFLICT(user_id) DO UPDATE SET balance = COALESCE(balance, 0) + ?',
            (user_id, amount, _now(), amount),
        )
        await conn.commit()
        async with conn.execute('SELECT balance FROM users WHERE user_id=?', (user_id,)) as cur:
            row = await cur.fetchone()
            return float(row[0]) if row and row[0] is not None else 0.0


async def set_balance(user_id, amount):
    async with aiosqlite.connect(DB_PATH) as conn:
        await conn.execute(
            'INSERT INTO users (user_id, balance, created_at) VALUES (?, ?, ?) '
            'ON CONFLICT(user_id) DO UPDATE SET balance = ?',
            (user_id, amount, _now(), amount),
        )
        await conn.commit()


async def get_discount(user_id):
    async with aiosqlite.connect(DB_PATH) as conn:
        async with conn.execute('SELECT discount FROM users WHERE user_id=?', (user_id,)) as cur:
            row = await cur.fetchone()
            return float(row[0]) if row and row[0] is not None else 0.0


async def set_discount(user_id, pct):
    async with aiosqlite.connect(DB_PATH) as conn:
        await conn.execute(
            'INSERT INTO users (user_id, discount, created_at) VALUES (?, ?, ?) '
            'ON CONFLICT(user_id) DO UPDATE SET discount = ?',
            (user_id, pct, _now(), pct),
        )
        await conn.commit()


async def count_users():
    async with aiosqlite.connect(DB_PATH) as conn:
        async with conn.execute('SELECT COUNT(*) FROM users') as cur:
            row = await cur.fetchone()
            return row[0] if row else 0


async def list_users(limit=8, offset=0):
    async with aiosqlite.connect(DB_PATH) as conn:
        conn.row_factory = aiosqlite.Row
        async with conn.execute(
            'SELECT user_id, username, full_name, language, balance, discount, created_at '
            'FROM users ORDER BY created_at DESC LIMIT ? OFFSET ?',
            (limit, offset),
        ) as cur:
            return [dict(r) for r in await cur.fetchall()]


async def get_all_users(limit=10, offset=0):
    '''Tuples for the admin panel: (user_id, username, full_name, balance, discount, created_at).'''
    async with aiosqlite.connect(DB_PATH) as conn:
        async with conn.execute(
            'SELECT user_id, username, full_name, balance, discount, created_at '
            'FROM users ORDER BY created_at DESC LIMIT ? OFFSET ?',
            (limit, offset),
        ) as cur:
            return await cur.fetchall()


async def get_all_orders(limit=10, offset=0, status=None):
    '''Tuples for the admin panel:
    (order_id, user_id, title, quantity, amount_usd, status, payment_method, created_at).'''
    async with aiosqlite.connect(DB_PATH) as conn:
        if status:
            q = ('SELECT order_id, user_id, title, quantity, amount_usd, status, payment_method, created_at '
                 'FROM orders WHERE status=? ORDER BY created_at DESC LIMIT ? OFFSET ?')
            p = (status, limit, offset)
        else:
            q = ('SELECT order_id, user_id, title, quantity, amount_usd, status, payment_method, created_at '
                 'FROM orders ORDER BY created_at DESC LIMIT ? OFFSET ?')
            p = (limit, offset)
        async with conn.execute(q, p) as cur:
            return await cur.fetchall()


async def find_user(query):
    '''Find a user by numeric id or @username. Returns dict or None.'''
    q = str(query or '').strip().lstrip('@')
    if not q:
        return None
    async with aiosqlite.connect(DB_PATH) as conn:
        conn.row_factory = aiosqlite.Row
        if q.isdigit():
            sql, p = 'SELECT * FROM users WHERE user_id=?', (int(q),)
        else:
            sql, p = 'SELECT * FROM users WHERE lower(username)=lower(?)', (q,)
        async with conn.execute(sql, p) as cur:
            row = await cur.fetchone()
            return dict(row) if row else None


async def stats():
    '''Aggregate numbers for the admin dashboard.'''
    out = {}
    async with aiosqlite.connect(DB_PATH) as conn:
        for key, sql in (
            ('users', 'SELECT COUNT(*) FROM users'),
            ('orders', 'SELECT COUNT(*) FROM orders'),
            ('orders_paid', "SELECT COUNT(*) FROM orders WHERE status IN ('paid','done')"),
            ('orders_pending', "SELECT COUNT(*) FROM orders WHERE status IN ('created','await_support')"),
            ('revenue', "SELECT COALESCE(SUM(amount_usd),0) FROM orders WHERE status IN ('paid','done')"),
            ('tickets_open', "SELECT COUNT(*) FROM tickets WHERE status='open'"),
            ('tickets_unread', "SELECT COALESCE(SUM(unread),0) FROM tickets WHERE status='open'"),
            ('leads_new', "SELECT COUNT(*) FROM leads WHERE status='new'"),
        ):
            async with conn.execute(sql) as cur:
                row = await cur.fetchone()
                out[key] = row[0] if row and row[0] is not None else 0
    return out


# ---------------- Support tickets ----------------
async def ticket_touch(user_id, direction, text, admin_id=None):
    '''Record a support message and update the ticket summary.

    direction: 'in'  = customer -> support (increments unread)
               'out' = support -> customer (resets unread)'''
    snippet = (text or '')[:300]
    async with aiosqlite.connect(DB_PATH) as conn:
        await conn.execute(
            'INSERT INTO support_messages (user_id, direction, admin_id, text, created_at) '
            'VALUES (?, ?, ?, ?, ?)',
            (user_id, direction, admin_id, text or '', _now()),
        )
        if direction == 'in':
            await conn.execute(
                'INSERT INTO tickets (user_id, status, unread, last_text, last_from, created_at, updated_at) '
                'VALUES (?, "open", 1, ?, "user", ?, ?) '
                'ON CONFLICT(user_id) DO UPDATE SET status="open", unread=unread+1, '
                'last_text=excluded.last_text, last_from="user", updated_at=excluded.updated_at',
                (user_id, snippet, _now(), _now()),
            )
        else:
            await conn.execute(
                'INSERT INTO tickets (user_id, status, unread, last_text, last_from, created_at, updated_at) '
                'VALUES (?, "open", 0, ?, "admin", ?, ?) '
                'ON CONFLICT(user_id) DO UPDATE SET unread=0, '
                'last_text=excluded.last_text, last_from="admin", updated_at=excluded.updated_at',
                (user_id, snippet, _now(), _now()),
            )
        await conn.commit()


async def ticket_close(user_id):
    async with aiosqlite.connect(DB_PATH) as conn:
        await conn.execute('UPDATE tickets SET status="closed", unread=0, updated_at=? WHERE user_id=?',
                           (_now(), user_id))
        await conn.commit()


async def ticket_get(user_id):
    async with aiosqlite.connect(DB_PATH) as conn:
        conn.row_factory = aiosqlite.Row
        async with conn.execute('SELECT * FROM tickets WHERE user_id=?', (user_id,)) as cur:
            row = await cur.fetchone()
            return dict(row) if row else None


async def tickets_list(status='open', limit=10, offset=0):
    '''Open tickets joined with user info, most recent first.'''
    async with aiosqlite.connect(DB_PATH) as conn:
        conn.row_factory = aiosqlite.Row
        async with conn.execute(
            'SELECT t.*, u.username, u.full_name FROM tickets t '
            'LEFT JOIN users u ON u.user_id = t.user_id '
            'WHERE t.status=? ORDER BY t.unread DESC, t.updated_at DESC LIMIT ? OFFSET ?',
            (status, limit, offset),
        ) as cur:
            return [dict(r) for r in await cur.fetchall()]


async def tickets_count(status='open'):
    async with aiosqlite.connect(DB_PATH) as conn:
        async with conn.execute('SELECT COUNT(*) FROM tickets WHERE status=?', (status,)) as cur:
            row = await cur.fetchone()
            return row[0] if row else 0


async def support_history(user_id, limit=15):
    '''Last N support messages for a user, oldest first.'''
    async with aiosqlite.connect(DB_PATH) as conn:
        async with conn.execute(
            'SELECT direction, admin_id, text, created_at FROM support_messages '
            'WHERE user_id=? ORDER BY id DESC LIMIT ?',
            (user_id, limit),
        ) as cur:
            rows = await cur.fetchall()
            return list(reversed(rows))


async def support_map_put(chat_id, message_id, user_id):
    '''Remember which customer a message in the staff chat belongs to.'''
    async with aiosqlite.connect(DB_PATH) as conn:
        await conn.execute(
            'INSERT OR REPLACE INTO support_map (chat_id, message_id, user_id) VALUES (?, ?, ?)',
            (chat_id, message_id, user_id),
        )
        await conn.commit()


async def support_map_get(chat_id, message_id):
    async with aiosqlite.connect(DB_PATH) as conn:
        async with conn.execute(
            'SELECT user_id FROM support_map WHERE chat_id=? AND message_id=?',
            (chat_id, message_id),
        ) as cur:
            row = await cur.fetchone()
            return int(row[0]) if row else None
