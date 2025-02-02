import requests
from bs4 import BeautifulSoup
import schedule
import time
import datetime
import os
from pytz import timezone

# === Налаштування ===
# Telegram Bot Token
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")  # Токен Telegram-бота (зчитується із середовища)

# Чат ID для надсилання повідомлень
CHAT_IDS = ["1037025457", "8171469284"]  # Список ID чатів, куди надсилати повідомлення

# URL сайту для перевірки новин
URL = "https://www.dar.gov.ua/news"

# Часовий пояс Києва
KYIV_TZ = timezone("Europe/Kiev")

# === Функції ===

def send_telegram_message(text):
    """
    Надсилання повідомлення у Telegram до всіх чатів із списку CHAT_IDS.
    """
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    for chat_id in CHAT_IDS:
        params = {"chat_id": chat_id, "text": text}
        response = requests.get(url, params=params)
        print(f"Message sent to {chat_id}. Response: {response.status_code} - {response.text}")

def check_news():
    """
    Перевіряє новини на сайті за цільовою датою (поточний день).
    Якщо знаходить новину з сьогоднішньою датою, надсилає повідомлення.
    """
    try:
        # Отримання HTML-сторінки
        response = requests.get(URL)
        soup = BeautifulSoup(response.text, "html.parser")

        # Пошук усіх дат новин на сторінці
        dates = soup.find_all("p", class_="paragraph-18 textadata")
        if not dates:
            print("Дати не знайдено. Можливо, структура сайту інша.")
            send_telegram_message("🔴 Дати не знайдено. Можливо, структура сайту інша.")
            return

        # Отримання поточної дати в Київському часі
        target_date = datetime.datetime.now(KYIV_TZ).strftime("%Y-%m-%d")
        print(f"Перевіряємо цільову дату: {target_date}")

        # Перевірка кожної знайденої дати
        for date_element in dates:
            date = date_element.text.strip()
            print(f"Перевіряємо дату: {date}")

            if date == target_date:  # Якщо дата збігається з цільовою
                send_telegram_message(f"🟢 Знайдено новину з датою {target_date}! Перевірте сайт: {URL}")
                print("Повідомлення надіслано.")
                return  # Зупиняємо перевірку після першого збігу

        # Якщо новини з сьогоднішньою датою не знайдено
        print(f"Новин з датою {target_date} не знайдено.")
    except Exception as e:
        print("Помилка у виконанні запиту або парсингу:", e)

def send_status_message():
    """
    Відправляє статусне повідомлення про роботу скрипта.
    """
    send_telegram_message("✅ Скрипт працює!")

# === Головний блок ===

# Надсилання повідомлення при запуску скрипта
send_status_message()

# Розклад завдань:
# 1. Перевірка новин кожні 20 хвилин
schedule.every(20).minutes.do(check_news)

# 2. Надсилання статусного повідомлення о 8:00 та 16:00 за Київським часом
schedule.every().day.at("08:00").do(send_status_message)
schedule.every().day.at("16:00").do(send_status_message)

# Основний цикл для виконання завдань за розкладом
while True:
    schedule.run_pending()
    time.sleep(600)  # Перевірка розкладу кожну секунду