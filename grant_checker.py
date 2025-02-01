import telebot
import os

# Встав свій API Token
BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Привіт!")

if __name__ == "__main__":
    bot.polling(none_stop=True)
