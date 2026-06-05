import os
import telebot
from datetime import datetime
from zoneinfo import ZoneInfo

TOKEN = os.getenv("BOT_TOKEN")

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(
        message,
        "🌍 نام شهر را بفرست\n\nمثال:\nLondon\nTokyo\nTehran\nNew York"
    )

@bot.message_handler(func=lambda m: True)
def get_time(message):
    cities = {
        "tehran": "Asia/Tehran",
        "london": "Europe/London",
        "paris": "Europe/Paris",
        "berlin": "Europe/Berlin",
        "moscow": "Europe/Moscow",
        "dubai": "Asia/Dubai",
        "tokyo": "Asia/Tokyo",
        "beijing": "Asia/Shanghai",
        "new york": "America/New_York",
        "los angeles": "America/Los_Angeles",
        "toronto": "America/Toronto",
        "sydney": "Australia/Sydney",
    }

    city = message.text.lower()

    if city in cities:
        now = datetime.now(ZoneInfo(cities[city]))
        bot.reply_to(
            message,
            f"🕒 ساعت {message.text.title()}\n\n{now.strftime('%Y-%m-%d %H:%M:%S')}"
        )
    else:
        bot.reply_to(message, "❌ شهر پیدا نشد")

bot.infinity_polling(skip_pending=True)
