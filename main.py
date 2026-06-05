import os
import telebot

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 927058267

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    user = message.from_user

    username = f"@{user.username}" if user.username else "ندارد"
    last_name = user.last_name if user.last_name else "ندارد"

    info = f"""
🚨 کاربر جدید وارد شد

👤 نام: {user.first_name}
📛 نام خانوادگی: {last_name}
🔗 یوزرنیم: {username}
🆔 آیدی: {user.id}
"""

    bot.send_message(ADMIN_ID, info)

    bot.reply_to(
        message,
        "سلام 👋\nبه ربات خوش اومدی."
    )

print("Bot is running...")
bot.infinity_polling(skip_pending=True)
