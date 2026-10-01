# Oncedshop Bot — деплой на Railway

Telegram-бот магазина (aiogram 3) + мини-апп + **встроенная поддержка**: покупатель пишет боту,
сообщение прилетает админу, админ отвечает — прямо из бота.

---

## Как работает поддержка

**Покупатель**
- Нажимает «📨 Поддержка» или просто пишет в бот любой текст / фото / чек.
- Видит «✅ Сообщение передано в поддержку». Ответ приходит в тот же чат от имени бота.

**Админ** (в ЛС с ботом или в группе поддержки)
- Получает карточку: `🆕 Сообщение от клиента · @user · id123` + кнопки
  **✉️ Ответить · 🕘 История · 🧾 Заказы клиента · 🔒 Закрыть**.
- Ответить можно тремя способами:
  1. **Reply (свайп) на карточку** — текст/фото/файл уйдёт клиенту.
  2. Кнопка **✉️ Ответить** → «режим ответа»: всё, что пишете дальше, идёт этому клиенту, пока не нажмёте
     «⏹ Завершить» или `/stop`.
  3. `/reply 123456789` или `/reply @username`.
- После отправки бот ставит 👍 на ваше сообщение (или пишет «Отправлено»).

**Команды админа**

| Команда | Что делает |
|---|---|
| `/admin` | Панель: статистика + кнопки Обращения / Заказы / Пользователи / Лиды |
| `/tickets` | Открытые обращения (🔴 — есть непрочитанные) |
| `/orders` | Заказы с кнопками «✅ Выдан», «✉️ Клиенту», «❌» |
| `/done ONC-XXXXXXXX` | Отметить заказ выданным (клиент получит уведомление) |
| `/users` | Пользователи, баланс, скидки |
| `/balance id +10` / `-5` / `=20` | Изменить баланс ($), клиент получит уведомление |
| `/discount id 10` | Персональная скидка в % |
| `/history id` | Последние 15 сообщений с клиентом |
| `/close id` | Закрыть обращение (клиенту придёт уведомление) |
| `/reply id`, `/stop` | Режим ответа |
| `/leads` | Лиды из мониторинга чатов (если включён Telethon) |
| `/score ссылка` | Задать/показать актуальный счёт CryptoBot для оплат (без аргумента — показать текущий) |

Уведомления об оплатах (Stars / баланс / «оплата у поддержки» / пополнение) тоже приходят
карточкой с кнопкой **📦 Выдан · ONC-…** — одно нажатие и клиент уведомлён.

---

## Деплой на Railway (10 минут)

### 1. Создайте бота
1. В Telegram откройте **@BotFather** → `/newbot` → придумайте имя и username.
2. Скопируйте **токен** (`123456:ABC-...`).
3. `/setmenubutton` → можно не трогать, команды бот выставит сам при старте.

### 2. Узнайте свой Telegram ID
Напишите любому боту `/id` — или запустите этого бота с пустым `ADMIN_IDS`, отправьте ему `/id`,
он ответит вашим ID. Это число нужно для `ADMIN_IDS`.

### 3. Загрузите код на GitHub
```bash
cd oncedshop_bot
git init
git add .
git commit -m "Oncedshop bot"
# создайте пустой репозиторий на github.com и:
git remote add origin https://github.com/<you>/oncedshop_bot.git
git push -u origin main
```
(альтернатива без GitHub — Railway CLI, см. ниже)

### 4. Создайте проект на Railway
1. [railway.app](https://railway.app) → **New Project → Deploy from GitHub repo** → выберите репозиторий.
2. Railway увидит `railway.json` / `nixpacks.toml` и соберёт Python 3.12, команда старта `python main.py`.

### 5. Переменные (Service → **Variables**)
Обязательные:
```
BOT_TOKEN      = токен из BotFather
ADMIN_IDS      = ваш Telegram ID (несколько — через запятую)
DB_PATH        = /data/oncedshop.db
```
Рекомендуемые:
```
ADMIN_USERNAME   = ваш username без @
SUPPORT_USERNAME = username поддержки без @ (для текстов)
WEBAPP_URL       = https://<ваш-домен>.up.railway.app   (см. шаг 7)
```
Опционально — группа поддержки, чтобы отвечала вся команда:
```
SUPPORT_CHAT_ID  = -1001234567890
```
(добавьте бота в группу, напишите там `/id` — он покажет Chat ID; в группе лучше отключить
у бота Privacy Mode в BotFather: `/setprivacy → Disable`, либо сделать его админом группы.)

### 6. Volume для базы (иначе БД сотрётся при каждом деплое)
Service → **Settings → Volumes → New Volume** → Mount path: `/data`.
`DB_PATH=/data/oncedshop.db` уже указывает туда.

### 7. Публичный домен для мини-аппа
Service → **Settings → Networking → Generate Domain**. Получите адрес вида
`https://oncedshop-bot-production.up.railway.app`.
Скопируйте его в переменную `WEBAPP_URL` — бот сам отдаёт `webapp/index.html` по этому адресу,
отдельный хостинг не нужен. После смены переменной Railway перезапустит сервис.

### 8. Проверка
- Откройте `https://<домен>/api/status` — должно быть `"bot_ready": true`, `"admins": 1`.
- В Telegram: `/start` боту → меню. Напишите «Привет» — вам как админу придёт карточка.
  Ответьте reply'ем — сообщение вернётся клиенту.
- `/admin` — панель.

---

## Railway CLI (без GitHub)
```bash
npm i -g @railway/cli
railway login
cd oncedshop_bot
railway init          # создать проект
railway up            # загрузить и задеплоить
railway variables --set BOT_TOKEN=... --set ADMIN_IDS=... --set DB_PATH=/data/oncedshop.db
railway domain        # выдать публичный домен → в WEBAPP_URL
```

---

## Локальный запуск
```bash
pip install -r requirements.txt
copy .env.example .env      # заполните BOT_TOKEN, ADMIN_IDS, DB_PATH=oncedshop.db
python main.py
```

## Структура
```
main.py        — точка входа, порядок роутеров, команды
support.py     — ПОДДЕРЖКА: доставка сообщений админам, ответы, тикеты, история
admin.py       — /admin, заказы, пользователи, баланс, скидки, лиды
handlers.py    — /start, язык, оплаты (Stars/баланс/крипта/CryptoBot), мои заказы
shopflow.py    — каталог и корзина внутри бота
orders.py      — сборка заказа (общая для мини-аппа и бота)
server.py      — aiohttp: отдаёт мини-апп, /api/order, /api/me, /api/topup, /api/status
database.py    — SQLite (users, orders, leads, tickets, support_messages, support_map)
common.py      — is_admin, фильтры IsAdmin/NotAdmin, esc()
keyboards.py   — клавиатуры и подписи кнопок
catalog.py     — товары и цены
monitor.py     — Telethon-монитор чатов (отдельный процесс, опционально)
```

## Частые вопросы
- **Сообщения клиентов никуда не приходят** — пусто `ADMIN_IDS` и `SUPPORT_CHAT_ID`. Отправьте боту `/id`
  и впишите число в `ADMIN_IDS`, редеплой.
- **`TelegramConflictError` в логах при деплое** — на 10–20 секунд старый и новый контейнер опрашивают Telegram
  одновременно. Само проходит.
- **База обнулилась** — не подключён Volume в `/data` (шаг 6).
- **Кнопка «🛒 Магазин» не показывается** — не задан `WEBAPP_URL`. Каталог внутри бота («📎 Каталог») работает без него.
- **Монитор чатов** (`monitor.py`) требует Telethon-сессию пользователя (см. `make_session.py`) и запускается
  отдельным сервисом Railway с тем же репозиторием и Start Command `python monitor.py`, с тем же Volume.
