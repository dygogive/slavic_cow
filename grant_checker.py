import requests
from flask import Flask, request
import schedule
import time
import datetime
from pytz import timezone
from bs4 import BeautifulSoup
from threading import Thread
import os

app = Flask(__name__)

# Токен Telegram бота
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
BASE_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"

# Список ID чатів
CHAT_IDS = ["1037025457", "8171469284"]

# URL сайту
URL = "https://www.dar.gov.ua/news"

# Часовий пояс Києва
KYIV_TZ = timezone("Europe/Kiev")

# Глобальний прапорець для контролю роботи бота
is_bot_running = True


def send_telegram_message(chat_id, text):
    """Функція для надсилання повідомлень."""
    url = f"{BASE_URL}/sendMessage"
    params = {"chat_id": chat_id, "text": text}
    response = requests.get(url, params=params)
    print(f"Message sent to {chat_id}. Response: {response.status_code} - {response.text}")


@app.route(f"/{TELEGRAM_BOT_TOKEN}", methods=["POST"])
def telegram_webhook():
    """Обробка вебхука Telegram."""
    global is_bot_running

    update = request.get_json()
    if "message" in update:
        chat_id = str(update["message"]["chat"]["id"])
        text = update["message"].get("text", "")

        if chat_id in CHAT_IDS:
            if text == "/start":
                if not is_bot_running:
                    is_bot_running = True
                    send_telegram_message(chat_id, "✅ Бот запущено!")
                else:
                    send_telegram_message(chat_id, "⚠️ Бот уже працює.")
            elif text == "/stop":
                if is_bot_running:
                    is_bot_running = False
                    send_telegram_message(chat_id, "⏹️ Бот зупинено.")
                else:
                    send_telegram_message(chat_id, "⚠️ Бот уже зупинено.")
            elif text == "/status":
                status = "працює" if is_bot_running else "зупинено"
                send_telegram_message(chat_id, f"ℹ️ Статус бота: {status}.")
            else:
                send_telegram_message(chat_id, "❓ Невідома команда. Використовуйте /start, /stop або /status.")
    return "OK", 200


def check_news():
    """Функція для перевірки новин."""
    global is_bot_running
    if not is_bot_running:
        return

    try:
        response = requests.get(URL)
        soup = BeautifulSoup(response.text, "html.parser")

        dates = soup.find_all("p", class_="paragraph-18 textadata")
        if not dates:
            print("Дати не знайдено. Можливо, структура сайту інша.")
            for chat_id in CHAT_IDS:
                send_telegram_message(chat_id, "🔴 Дати не знайдено. Можливо, структура сайту інша.")
            return

        target_date = datetime.datetime.now(KYIV_TZ).strftime("%Y-%m-%d")
        print(f"Перевіряємо цільову дату: {target_date}")

        found = False
        for date_element in dates:
            date = date_element.text.strip()
            print(f"Перевіряємо дату: {date}")

            if date == target_date:
                for chat_id in CHAT_IDS:
                    send_telegram_message(chat_id, f"🟢 Знайдено новину з датою {target_date}! Перевірте сайт: {URL}")
                found = True
                return

        if not found:
            print(f"Новин з датою {target_date} не знайдено.")
    except Exception as e:
        print("Помилка у виконанні запиту або парсингу:", e)


def send_status_message():
    """Надсилання статусного повідомлення."""
    for chat_id in CHAT_IDS:
        send_telegram_message(chat_id, "✅ Скрипт працює!")


def run_schedule():
    """Функція для запуску розкладу."""
    schedule.every(10).minutes.do(check_news)
    schedule.every().day.at("08:00").do(send_status_message)
    schedule.every().day.at("17:00").do(send_status_message)

    while True:
        schedule.run_pending()
        time.sleep(1)


# Запуск розкладу в окремому потоці
if __name__ != "__main__":
    thread = Thread(target=run_schedule)
    thread.start()
