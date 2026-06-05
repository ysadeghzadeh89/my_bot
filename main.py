import os
import telebot
from datetime import datetime
from zoneinfo import ZoneInfo

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 927058267

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    user = message.from_user

    bot.send_message(
        ADMIN_ID,
        f"""
🚨 کاربر جدید

👤 نام: {user.first_name}
🆔 آیدی: {user.id}
🔗 یوزرنیم: @{user.username}
"""
    )

    capitals = {
        "تهران": "Asia/Tehran",
        "لندن": "Europe/London",
        "پاریس": "Europe/Paris",
        "برلین": "Europe/Berlin",
        "مسکو": "Europe/Moscow",
        "دبی": "Asia/Dubai",
        "توکیو": "Asia/Tokyo",
        "نیویورک": "America/New_York",
        "تورنتو": "America/Toronto",
    }

    text = "🌍⌚️ ساعت پایتخت‌های مهم:\n\n"

    for city, tz in capitals.items():
        now = datetime.now(ZoneInfo(tz))
        text += f"{city}⌚️: {now.strftime('%H:%M:%S')}\n"

    bot.send_message(message.chat.id, text)

bot.infinity_polling(skip_pending=True)
