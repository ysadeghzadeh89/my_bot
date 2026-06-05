import os
import telebot
import requests
from bs4 import BeautifulSoup

TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

def get_usd():
    try:
        url = "https://api.exchangerate.host/latest?base=USD&symbols=IRR"
        data = requests.get(url, timeout=10).json()
        return int(data["rates"]["IRR"])
    except:
        return None


def get_gold():
    try:
        url = "https://www.tgju.org/profile/geram18"
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(url, headers=headers, timeout=10)

        soup = BeautifulSoup(r.text, "html.parser")

        price = soup.find("span", {"data-col": "info.last_trade.PDrCotVal"})
        if price:
            return price.text.strip()
        return "نامشخص"
    except:
        return "خطا در دریافت"


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id,
        "👋 سلام\n\n/price\n/dollar\n/gold"
    )


@bot.message_handler(commands=['price'])
def price(message):
    usd = get_usd()
    gold = get_gold()

    text = "📊 قیمت لحظه‌ای:\n\n"

    text += f"💵 دلار: {usd:,} ریال\n" if usd else "💵 دلار: خطا\n"
    text += f"🪙 طلا 18: {gold} تومان\n"

    bot.send_message(message.chat.id, text)


@bot.message_handler(commands=['dollar'])
def dollar(message):
    usd = get_usd()
    bot.send_message(message.chat.id, f"💵 {usd:,}" if usd else "خطا")


@bot.message_handler(commands=['gold'])
def gold(message):
    bot.send_message(message.chat.id, f"🪙 {get_gold()}")


bot.infinity_polling(skip_pending=True)
