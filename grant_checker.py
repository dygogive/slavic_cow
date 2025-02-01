import telebot

# Вкажіть ваш API-токен
bot = telebot.TeleBot('TELEGRAM_BOT_TOKEN')

@bot.message_handler(content_types=['text', 'document', 'audio'])
def get_text_messages(message):
    if message.text == "/start":
        bot.send_message(message.chat.id, "Відповідає на старт")
    elif message.text == "/help":
        bot.send_message(message.chat.id, "Відповідає на хелп")

# Запуск бота
if __name__ == "__main__":
    bot.polling(none_stop=True, interval=0)
