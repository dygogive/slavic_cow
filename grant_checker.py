import requests
from flask import Flask, request
import schedule
import time
import datetime
from pytz import timezone
from bs4 import BeautifulSoup
import os

app = Flask(__name__)

# Токен Telegram бота
TELEGRAM_BOT_TOKEN = "7633507105:AAEqMB0ETZCK1VZ3ccgaj7yor4KUK88bZcY"
BASE_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"

# Глобальна змінна для зберігання `chat_id`
CHAT_ID = None

# URL сайту
URL = "https://www.dar.gov.ua/news"

# Часовий пояс Києва
KYIV_TZ = timezone("Europe/Kiev")


def send_telegram_message(chat_id, text):
    """Функція для надсилання повідомлення через Telegram API."""
    url = f"{BASE_URL}/sendMessage"
    params = {"chat_id": chat_id, "text": text}
    response = requests.get(url, params=params)
    print(f"Telegram API Response: {response.status_code} - {response.text}")


@app.route(f"/{TELEGRAM_BOT_TOKEN}", methods=["POST"])
def telegram_webhook():
    """Обробка вебхуків Telegram."""
    global CHAT_ID

    update = request.get_json()
    if "message" in update:
        chat_id = update["message"]["chat"]["id"]
        text = update["message"].get("text", "")

        if text == "/start":
            CHAT_ID = chat_id
            send_telegram_message(CHAT_ID, "Бот успішно активовано. Ваш чат готовий для отримання повідомлень.")
        else:
            send_telegram_message(chat_id, "Будь ласка, введіть /start для активації бота.")

    return "OK", 200


def check_news():
    """Функція перевірки новин."""
    global CHAT_ID
    if CHAT_ID is None:
        print("CHAT_ID не встановлений. Спочатку виконайте /start.")
        return

    try:
        response = requests.get(URL)
        soup = BeautifulSoup(response.text, "html.parser")
        dates = soup.find_all("p", class_="paragraph-18 textadata")

        if not dates:
            print("Дати не знайдено. Можливо, структура сайту інша.")
            send_telegram_message(CHAT_ID, "🔴 Не знайдено дат на сайті. Можливо, структура сайту змінилася.")
            return

        target_date = datetime.datetime.now(KYIV_TZ).strftime("%Y-%m-%d")
        print(f"Перевіряємо новини за датою: {target_date}")

        for date_element in dates:
            date = date_element.text.strip()
            if date == target_date:
                send_telegram_message(CHAT_ID, f"🟢 Новина з датою {target_date} знайдена! Перевірте сайт: {URL}")
                return

        print(f"Новин з датою {target_date} не знайдено.")
    except Exception as e:
        print(f"Помилка: {e}")


def send_status_message():
    """Функція для надсилання статусного повідомлення."""
    global CHAT_ID
    if CHAT_ID:
        send_telegram_message(CHAT_ID, "✅ Бот працює.")
    else:
        print("CHAT_ID не встановлений. Статусне повідомлення не надіслано.")


def set_webhook():
    """Функція для налаштування вебхука Telegram."""
    webhook_url = f"https://{os.getenv('RAILWAY_STATIC_URL')}/{TELEGRAM_BOT_TOKEN}"
    url = f"{BASE_URL}/setWebhook"
    response = requests.post(url, data={"url": webhook_url})
    print(f"Set webhook response: {response.status_code} - {response.text}")


# Запуск завдань за розкладом
schedule.every(10).minutes.do(check_news)
schedule.every().day.at("08:00").do(send_status_message)
schedule.every().day.at("17:00").do(send_status_message)

def run_schedule():
    """Функція для запуску розкладу в окремому потоці."""
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    # Встановити вебхук, якщо це необхідно
    if os.getenv("SET_WEBHOOK") == "true":
        set_webhook()

    # Запуск Flask додатку
    from threading import Thread
    schedule_thread = Thread(target=run_schedule)
    schedule_thread.start()

    app.run(host="0.0.0.0", port=i
