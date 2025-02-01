import requests
from bs4 import BeautifulSoup
import schedule
import time
import datetime
import os
from threading import Thread
from pytz import timezone

# Токен і Chat ID для Telegram
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Список ID чатів
CHAT_ID_1 = "1037025457"
CHAT_ID_2 = "8171469284"
CHAT_IDS = [CHAT_ID_1, CHAT_ID_2]  

# URL сайту
URL = "https://www.dar.gov.ua/news"

# Часовий пояс Києва
KYIV_TZ = timezone("Europe/Kiev")

# Глобальний прапорець для контролю роботи бота
is_bot_running = False

def send_telegram_message(text):
    """Функція для надсилання повідомлень усім чатам."""
    for chat_id in CHAT_IDS:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        params = {"chat_id": chat_id, "text": text}
        response = requests.get(url, params=params)
        print(f"Message sent to {chat_id}. Response: {response.status_code} - {response.text}")

def check_news():
    """Функція для перевірки новин."""
    global is_bot_running
    if not is_bot_running:
        return

    try:
        response = requests.get(URL)
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Знайти всі дати на сторінці
        dates = soup.find_all("p", class_="paragraph-18 textadata")

        if not dates:
            print("Дати не знайдено. Можливо, структура сайту інша.")
            send_telegram_message("🔴 Дати не знайдено. Можливо, структура сайту інша.")
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
                send_telegram_message(f"🟢 Знайдено новину з датою {target_date}! Перевірте сайт: {URL}")
                print("Повідомлення надіслано.")
                found = True
                return  # Зупинити перевірку після першої знайденої новини

        # Якщо новина не знайдена
        if not found:
            print(f"Новин з датою {target_date} не знайдено.")
    except Exception as e:
        print("Помилка у виконанні запиту або парсингу:", e)

def send_status_message():
    """Функція для надсилання статусного повідомлення."""
    send_telegram_message("✅ Скрипт працює!")

def handle_commands():
    """Функція для обробки команд із Telegram."""
    global is_bot_running

    last_update_id = None
    while True:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getUpdates"
        params = {"offset": last_update_id, "timeout": 10}
        response = requests.get(url, params=params)
        updates = response.json()["result"]

        for update in updates:
            last_update_id = update["update_id"] + 1
            if "message" in update:
                chat_id = str(update["message"]["chat"]["id"])
                text = update["message"].get("text", "")

                if chat_id in CHAT_IDS:
                    if text == "/start":
                        if not is_bot_running:
                            is_bot_running = True
                            send_telegram_message("✅ Бот запущено!")
                        else:
                            send_telegram_message("⚠️ Бот уже працює.")
                    elif text == "/stop":
                        if is_bot_running:
                            is_bot_running = False
                            send_telegram_message("⏹️ Бот зупинено.")
                        else:
                            send_telegram_message("⚠️ Бот уже зупинено.")
                    elif text == "/status":
                        status = "працює" if is_bot_running else "зупинено"
                        send_telegram_message(f"ℹ️ Статус бота: {status}.")
                    else:
                        send_telegram_message("❓ Невідома команда. Використовуйте /start, /stop або /status.")

def run_schedule():
    """Функція для запуску розкладу."""
    while True:
        schedule.run_pending()
        time.sleep(1)

# Надсилання повідомлення при запуску
send_telegram_message("✅ Скрипт запущено!")

# Запуск перевірки новин кожні 10 хвилин
schedule.every(10).minutes.do(check_news)

# Надсилання повідомлення про статус
schedule.every().day.at("08:00").do(send_status_message)
schedule.every().day.at("17:00").do(send_status_message)

# Запуск багатопоточності для обробки команд і розкладу
if __name__ == "__main__":
    Thread(target=handle_commands).start()
    Thread(target=run_schedule).start()
