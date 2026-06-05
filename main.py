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

    username = f"@{user.username}" if user.username else "ندارد"
    last_name = user.last_name if user.last_name else "ندارد"

    info = f"""
🚨 کاربر جدید

👤 نام: {user.first_name}
📛 نام خانوادگی: {last_name}
🔗 یوزرنیم: {username}
🆔 آیدی: {user.id}
"""

    bot.send_message(ADMIN_ID, info)

    capitals = {
        "🇮🇷 تهران": "Asia/Tehran",
        "🇬🇧 لندن": "Europe/London",
        "🇫🇷 پاریس": "Europe/Paris",
        "🇩🇪 برلین": "Europe/Berlin",
        "🇷🇺 مسکو": "Europe/Moscow",
        "🇦🇪 ابوظبی": "Asia/Dubai",
        "🇨🇳 پکن": "Asia/Shanghai",
        "🇯🇵 توکیو": "Asia/Tokyo",
        "🇺🇸 واشنگتن": "America/New_York",
        "🇨🇦 اتاوا": "America/Toronto",
        "🇦🇺 کانبرا": "Australia/Sydney",
    }

    text = "🌍 ساعت پایتخت‌های جهان\n\n"

    for city, tz in capitals.items():
        now = datetime.now(ZoneInfo(tz))
        text += f"{city}: {now.strftime('%H:%M:%S')}\n"

    bot.send_message(message.chat.id, text)

bot.infinity_polling(skip_pending=True)
