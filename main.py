import os
import telebot
import sqlite3
import random
from datetime import datetime
active_bet = None
TOKEN = os.getenv("BOT_TOKEN")

bot = telebot.TeleBot(TOKEN)

db = sqlite3.connect("economy.db", check_same_thread=False)
cursor = db.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
    user_id INTEGER PRIMARY KEY,
    name TEXT,
    balance INTEGER DEFAULT 1000,
    last_daily TEXT DEFAULT '',
    luck INTEGER DEFAULT 0
)
""")
db.commit()


def get_user(user):
    cursor.execute("SELECT * FROM users WHERE user_id=?", (user.id,))
    data = cursor.fetchone()

    if not data:
        cursor.execute(
            "INSERT INTO users(user_id,name,balance,luck) VALUES(?,?,?,?)",
            (user.id, user.first_name, 1000, 0)
        )
        db.commit()

        cursor.execute("SELECT * FROM users WHERE user_id=?", (user.id,))
        data = cursor.fetchone()

    return data


@bot.message_handler(commands=["start"])
def start(message):
    get_user(message.from_user)
    bot.reply_to(message,
        "💰 ربات اقتصاد فعال شد!\n\n"
        "/balance\n"
        "/daily\n"
        "/bet 100\n"
        "/buy\n"
        "/luck\n"
        "/top\n"
        "/balances\n"
    )


@bot.message_handler(commands=["balance"])
def balance(message):
    user = get_user(message.from_user)
    bot.reply_to(message, f"💰 موجودی: {user[2]} سکه")


@bot.message_handler(commands=["daily"])
def daily(message):

    user = get_user(message.from_user)
    today = datetime.now().strftime("%Y-%m-%d")

    if user[3] == today:
        bot.reply_to(message, "⛔ امروز گرفتی")
        return

    reward = random.randint(100, 500)

    cursor.execute(
        "UPDATE users SET balance=balance+?, last_daily=? WHERE user_id=?",
        (reward, today, message.from_user.id)
    )
    db.commit()

    bot.reply_to(message, f"🎁 +{reward} سکه")


# 🛒 SHOP
@bot.message_handler(commands=["buy"])
def buy(message):

    items = {
        "clover": (5000, 5),
        "hat": (15000, 10),
        "diamond": (50000, 20),
        "crown": (200000, 30)
    }

    try:
        item = message.text.split()[1].lower()
    except:
        bot.reply_to(message,
            "🛒 فروشگاه:\n"
            "/buy clover 🍀\n"
            "/buy hat 🎩\n"
            "/buy diamond 💎\n"
            "/buy crown 👑"
        )
        return

    if item not in items:
        bot.reply_to(message, "❌ آیتم نیست")
        return

    price, luck = items[item]
    user = get_user(message.from_user)

    if user[2] < price:
        bot.reply_to(message, "❌ پول نداری")
        return

    cursor.execute(
        "UPDATE users SET balance=balance-?, luck=luck+? WHERE user_id=?",
        (price, luck, message.from_user.id)
    )
    db.commit()

    bot.reply_to(message, f"✅ خرید شد +{luck}% شانس")


# 🍀 LUCK
@bot.message_handler(commands=["luck"])
def luck(message):

    cursor.execute(
        "SELECT luck FROM users WHERE user_id=?",
        (message.from_user.id,)
    )

    l = cursor.fetchone()[0]

    bot.reply_to(message, f"🍀 شانس: {l}%")


# 🎲 BET
@bot.message_handler(commands=["bet"])
def bet(message):

    try:
        amount = int(message.text.split()[1])
    except:
        bot.reply_to(message, "مثال:\n/bet 500")
        return

    cursor.execute(
        "SELECT balance,luck FROM users WHERE user_id=?",
        (message.from_user.id,)
    )

    data = cursor.fetchone()
    balance = data[0]
    luck = data[1]

    if amount <= 0:
        return

    if balance < amount:
        bot.reply_to(message, "❌ موجودی کافی نیست")
        return

    chance = min(85, 50 + luck)

    if random.randint(1, 100) <= chance:

        cursor.execute(
            "UPDATE users SET balance=balance+? WHERE user_id=?",
            (amount, message.from_user.id)
        )
        db.commit()

        bot.reply_to(message,
            f"🏆 بردی!\n💰 +{amount}\n🍀 شانس: {chance}%"
        )

    else:

        cursor.execute(
            "UPDATE users SET balance=balance-? WHERE user_id=?",
            (amount, message.from_user.id)
        )
        db.commit()

        bot.reply_to(message,
            f"💀 باختی!\n💸 -{amount}\n🍀 شانس: {chance}%"
        )


# 🏆 TOP
@bot.message_handler(commands=["top"])
def top(message):

    cursor.execute(
        "SELECT name,balance FROM users ORDER BY balance DESC LIMIT 10"
    )

    users = cursor.fetchall()

    text = "🏆 برترین‌ها:\n\n"

    for i, u in enumerate(users, 1):
        text += f"{i}. {u[0]} — {u[1]}\n"

    bot.send_message(message.chat.id, text)

ADMIN_ID = 927058267

@bot.message_handler(func=lambda m: m.text == "پول مخفی")
def secret_money(message):

    if message.from_user.id != ADMIN_ID:
        return

    cursor.execute(
        "UPDATE users SET balance = balance + 500000 WHERE user_id = ?",
        (message.from_user.id,)
    )

    db.commit()

    bot.reply_to(
        message,
        "💰 500000 سکه به حسابت اضافه شد!"
    )
@bot.message_handler(commands=["betuser"])
def betuser(message):

    global active_bet

    if active_bet:
        bot.reply_to(message, "❌ یک شرط در حال انتظار است")
        return

    try:
        amount = int(message.text.split()[1])
    except:
        bot.reply_to(message, "مثال:\n/betuser 500")
        return

    user = get_user(message.from_user)

    if user[2] < amount:
        bot.reply_to(message, "❌ موجودی کافی نیست")
        return

    active_bet = {
        "creator": message.from_user.id,
        "creator_name": message.from_user.first_name,
        "amount": amount
    }

    bot.send_message(
        message.chat.id,
        f"🎲 {message.from_user.first_name} یک شرط {amount} سکه‌ای ساخت!\n\n/accept"
    )


@bot.message_handler(commands=["accept"])
def accept(message):

    global active_bet

    if not active_bet:
        return

    if message.from_user.id == active_bet["creator"]:
        return

    amount = active_bet["amount"]

    cursor.execute(
        "SELECT balance FROM users WHERE user_id=?",
        (message.from_user.id,)
    )

    row = cursor.fetchone()

    if not row or row[0] < amount:
        bot.reply_to(message, "❌ موجودی کافی نداری")
        return

    roll1 = random.randint(1, 6)
    roll2 = random.randint(1, 6)

    if roll1 > roll2:

        winner = active_bet["creator"]
        winner_name = active_bet["creator_name"]

    elif roll2 > roll1:

        winner = message.from_user.id
        winner_name = message.from_user.first_name

    else:

        bot.send_message(
            message.chat.id,
            f"🤝 مساوی شد!\n🎲 {roll1} - {roll2}"
        )

        active_bet = None
        return

    loser = message.from_user.id if winner == active_bet["creator"] else active_bet["creator"]

    cursor.execute(
        "UPDATE users SET balance=balance-? WHERE user_id=?",
        (amount, loser)
    )

    cursor.execute(
        "UPDATE users SET balance=balance+? WHERE user_id=?",
        (amount, winner)
    )

    db.commit()

    bot.send_message(
        message.chat.id,
        f"⚔️ نتیجه شرط\n\n"
        f"{active_bet['creator_name']} 🎲 {roll1}\n"
        f"{message.from_user.first_name} 🎲 {roll2}\n\n"
        f"🏆 برنده: {winner_name}\n"
        f"💰 +{amount} سکه"
    )

    active_bet = None
@bot.message_handler(commands=["start"])
def start(message):
    user_id = message.from_user.id
    name = message.from_user.first_name

    cursor.execute("SELECT * FROM users WHERE id=?", (user_id,))
    user = cursor.fetchone()

    if user is None:
        cursor.execute(
            "INSERT INTO users (id, name, balance, luck) VALUES (?, ?, ?, ?)",
            (user_id, name, 1000, 10)
        )
        conn.commit()

    bot.send_message(message.chat.id, "خوش اومدی 👋")
@bot.message_handler(commands=["balances"])
def balances(message):

    cursor.execute("SELECT name, balance, luck FROM users ORDER BY balance DESC")
    users = cursor.fetchall()

    if not users:
        bot.send_message(message.chat.id, "هیچ بازیکنی هنوز ثبت نشده ❌")
        return

    text = "🏦 وضعیت بازیکنان:\n\n"

    for i, (name, balance, luck) in enumerate(users, 1):
        text += f"{i}. {name}\n💰 {balance:,} | 🍀 {luck}%\n\n"

    bot.send_message(message.chat.id, text)
bot.infinity_polling(skip_pending=True)
