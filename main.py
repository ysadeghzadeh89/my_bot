import os
import telebot
import sqlite3
import random
from datetime import datetime

TOKEN = os.getenv("BOT_TOKEN")

bot = telebot.TeleBot(TOKEN)

db = sqlite3.connect("economy.db", check_same_thread=False)
cursor = db.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
    user_id INTEGER PRIMARY KEY,
    name TEXT,
    balance INTEGER DEFAULT 1000,
    last_daily TEXT
)
""")
db.commit()

def get_user(user):
    cursor.execute(
        "SELECT * FROM users WHERE user_id=?",
        (user.id,)
    )
    data = cursor.fetchone()

    if not data:
        cursor.execute(
            "INSERT INTO users(user_id,name,balance) VALUES(?,?,?)",
            (user.id, user.first_name, 1000)
        )
        db.commit()

        cursor.execute(
            "SELECT * FROM users WHERE user_id=?",
            (user.id,)
        )
        data = cursor.fetchone()

    return data

@bot.message_handler(commands=["start"])
def start(message):
    get_user(message.from_user)

    bot.reply_to(
        message,
        "💰 اقتصاد گروه فعال شد!\n\n"
        "/balance\n"
        "/daily\n"
        "/bet مبلغ\n"
        "/top"
    )

@bot.message_handler(commands=["balance"])
def balance(message):
    user = get_user(message.from_user)

    bot.reply_to(
        message,
        f"💰 موجودی شما: {user[2]} سکه"
    )

@bot.message_handler(commands=["daily"])
def daily(message):
    user = get_user(message.from_user)

    today = datetime.now().strftime("%Y-%m-%d")

    if user[3] == today:
        bot.reply_to(
            message,
            "⛔ جایزه امروزت رو گرفتی"
        )
        return

    reward = random.randint(100, 500)

    cursor.execute(
        "UPDATE users SET balance=balance+?, last_daily=? WHERE user_id=?",
        (reward, today, message.from_user.id)
    )
    db.commit()

    bot.reply_to(
        message,
        f"🎁 جایزه روزانه: {reward} سکه"
    )

@bot.message_handler(commands=["bet"])
def bet(message):
    try:
        amount = int(message.text.split()[1])
    except:
        bot.reply_to(message, "مثال:\n/bet 500")
        return

    user = get_user(message.from_user)

    if amount <= 0:
        return

    if user[2] < amount:
        bot.reply_to(message, "❌ موجودی کافی نیست")
        return

    if random.randint(1, 100) <= 50:

        cursor.execute(
            "UPDATE users SET balance=balance+? WHERE user_id=?",
            (amount, message.from_user.id)
        )

        db.commit()

        bot.reply_to(
            message,
            f"🏆 بردی!\n+{amount} سکه"
        )

    else:

        cursor.execute(
            "UPDATE users SET balance=balance-? WHERE user_id=?",
            (amount, message.from_user.id)
        )

        db.commit()

        bot.reply_to(
            message,
            f"💀 باختی!\n-{amount} سکه"
        )

@bot.message_handler(commands=["top"])
def top(message):

    cursor.execute(
        "SELECT name,balance FROM users ORDER BY balance DESC LIMIT 10"
    )

    users = cursor.fetchall()

    text = "🏆 ثروتمندترین کاربران:\n\n"

    for i, user in enumerate(users, start=1):
        text += f"{i}. {user[0]} — {user[1]} سکه\n"

    bot.send_message(message.chat.id, text)

bot.infinity_polling(skip_pending=True)
