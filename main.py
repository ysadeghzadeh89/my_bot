import telebot
import requests

TOKEN = "8923305310:AAG1fS-vOvHjw2xHIelTrTz-zs_BZHGJziY"

bot = telebot.TeleBot(TOKEN)

def get_usd():
    try:
        url = "https://api.exchangerate.host/latest?base=USD&symbols=IRR"
        data = requests.get(url).json()
        return int(data["rates"]["IRR"])
    except:
        return None

def get_gold():
    return "18,250,000"

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id,
        "👋 سلام!\n\n/price\n/dollar\n/gold"
    )

@bot.message_handler(commands=['price'])
def price(message):
    usd = get_usd()
    text = "📊\n\n"
    if usd:
        text += f"💵 دلار: {usd:,} ریال\n"
    else:
        text += "💵 دلار: خطا\n"
    text += f"🪙 طلا: {get_gold()} تومان"
    bot.send_message(message.chat.id, text)

@bot.message_handler(commands=['dollar'])
def dollar(message):
    usd = get_usd()
    bot.send_message(message.chat.id, f"💵 {usd:,}" if usd else "خطا")

@bot.message_handler(commands=['gold'])
def gold(message):
    bot.send_message(message.chat.id, f"🪙 {get_gold()}")

bot.infinity_polling()
