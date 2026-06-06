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
@bot.message_handler(commands=["pay"])
def pay(message):
    try:
        target_id = int(message.text.split()[1])
        amount = int(message.text.split()[2])
    except:
        bot.reply_to(message, "مثال:\n/pay 123456789 500")
        return

    sender = get_user(message.from_user)

    if amount <= 0:
        return

    if sender[2] < amount:
        bot.reply_to(message, "❌ موجودی کافی نیست")
        return

    cursor.execute(
        "SELECT * FROM users WHERE user_id=?",
        (target_id,)
    )

    target = cursor.fetchone()

    if not target:
        bot.reply_to(message, "❌ کاربر پیدا نشد")
        return

    cursor.execute(
        "UPDATE users SET balance=balance-? WHERE user_id=?",
        (amount, message.from_user.id)
    )

    cursor.execute(
        "UPDATE users SET balance=balance+? WHERE user_id=?",
        (amount, target_id)
    )

    db.commit()

    bot.reply_to(
        message,
        f"💸 {amount} سکه انتقال یافت"
    )

@bot.message_handler(commands=["work"])
def work(message):

    reward = random.randint(50, 300)

    jobs = [
        "🍕 پیک موتوری شدی",
        "💻 برنامه نوشتی",
        "⚽ مربی فوتبال شدی",
        "🚕 مسافر جابه‌جا کردی",
        "🏗 کار ساختمانی کردی"
    ]

    cursor.execute(
        "UPDATE users SET balance=balance+? WHERE user_id=?",
        (reward, message.from_user.id)
    )

    db.commit()

    bot.reply_to(
        message,
        f"{random.choice(jobs)}\n\n💰 +{reward} سکه"
    )

@bot.message_handler(commands=["profile"])
def profile(message):

    user = get_user(message.from_user)

    bot.reply_to(
        message,
        f"""
👤 نام: {message.from_user.first_name}

🆔 {message.from_user.id}

💰 موجودی: {user[2]} سکه
"""
    )

@bot.message_handler(commands=["dice"])
def dice(message):

    win = random.randint(1, 6)

    reward = win * 50

    cursor.execute(
        "UPDATE users SET balance=balance+? WHERE user_id=?",
        (reward, message.from_user.id)
    )

    db.commit()

    bot.reply_to(
        message,
        f"🎲 تاس: {win}\n💰 جایزه: {reward}"
    )

@bot.message_handler(commands=["rob"])
def rob(message):

    cursor.execute(
        "SELECT user_id,name,balance FROM users ORDER BY RANDOM() LIMIT 1"
    )

    target = cursor.fetchone()

    if not target:
        return

    if target[0] == message.from_user.id:
        bot.reply_to(message, "😅 امروز کسی برای دزدی پیدا نشد")
        return

    amount = random.randint(50, 300)

    if random.randint(1, 100) <= 50:

        cursor.execute(
            "UPDATE users SET balance=balance+? WHERE user_id=?",
            (amount, message.from_user.id)
        )

        cursor.execute(
            "UPDATE users SET balance=MAX(balance-?,0) WHERE user_id=?",
            (amount, target[0])
        )

        db.commit()

        bot.reply_to(
            message,
            f"😈 دزدی موفق!\n💰 +{amount} سکه"
        )

    else:

        cursor.execute(
            "UPDATE users SET balance=balance-? WHERE user_id=?",
            (amount, message.from_user.id)
        )

        db.commit()

        bot.reply_to(
            message,
            f"🚔 پلیس گرفتت!\n💸 -{amount} سکه"
        )
bot.infinity_polling(skip_pending=True)
