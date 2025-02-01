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
    url = f"{BASE_URL}/sendMessage"
    params = {"chat_id": chat_id, "text": text}
    response = requests.get(url, params=params)
    print(f"Telegram API Response: {response.status_code} - {response.text}")


@app.route(f"/{TELEGRAM_BOT_TOKEN}", methods=["POST"])
def telegram_webhook():
    global CHAT_ID

    update = request.get_json()
    if "message" in update:
        chat_id = update["message"]["chat"]["id"]
        text = update["message"].get("text", "")

        # Якщо отримана команда /start
        if text == "/start":
            CHAT_ID = chat_id
            send_telegram_message(CHAT_ID, f"Ваш chat_id: {CHAT_ID}. Бот готовий працювати!")
        else:
            send_telegram_message(chat_id, "Будь ласка, введіть /start, щоб активувати бота.")

    return "OK", 200


def check_news():
    if CHAT_ID is None:
        print("CHAT_ID не встановлений. Спочатку виконайте /start.")
        return

    try:
        response = requests.get(URL)
        soup = BeautifulSoup(response.text, "html.parser")

        # Знайти всі дати на сторінці
        dates = soup.find_all("p", class_="paragraph-18 textadata")

        if not dates:
            print("Дати не знайдено. Можливо, структура сайту інша.")
            send_telegram_message(CHAT_ID, "🔴 Дати не знайдено. Можливо, структура сайту інша.")
            return

        # Цільова дата
        target_date = datetime.datetime.now(KYIV_TZ).strftime("%Y-%m-%d")
        print(f"Перевіряємо цільову дату: {target_date}")

        found = False  # Прапорець для перевірки, чи була знайдена новина

        for date_element in dates:
            date = date_element.text.strip()
            print(f"Перевіряємо дату: {date}")

            # Якщо дата збігається з цільовою
            if date == target_date:
                send_telegram_message(CHAT_ID, f"🟢 Знайдено новину з датою {target_date}! Перевірте сайт: {URL}")
                print("Повідомлення надіслано.")
                found = True
                return  # Зупинити перевірку після першої знайденої новини

        # Якщо новина не знайдена
        if not found:
            print(f"Новин з датою {target_date} не знайдено.")
    except Exception as e:
        print("Помилка у виконанні запиту або парсингу:", e)


def send_status_message():
    if CHAT_ID:
        send_telegram_message(CHAT_ID, "✅ Скрипт працює!")
    else:
        print("CHAT_ID не встановлений. Статусне повідомлення не надіслано.")


# Встановити вебхук (викликається лише вручну)
def set_webhook():
    url = f"{BASE_URL}/setWebhook"
    webhook_url = f"https://{os.getenv('RAILWAY_STATIC_URL')}/{TELEGRAM_BOT_TOKEN}"
    response = requests.post(url, data={"url": webhook_url})
    print(f"Set webhook response: {response.status_code} - {response.text}")


# Надсилання статусних повідомлень за розкладом
schedule.every(10).minutes.do(check_news)
schedule.every().day.at("08:00").do(send_status_message)
schedule.every().day.at("17:00").do(send_status_message)

if __name__ == "__main__":
    # Увімкніть виклик set_webhook вручну, коли потрібно
    if os.getenv("SET_WEBHOOK") == "true":
        set_webhook()

    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
