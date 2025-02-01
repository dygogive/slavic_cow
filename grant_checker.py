import requests
from bs4 import BeautifulSoup
import schedule
import time
import datetime
import os

# Токен і Chat ID для Telegram
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = "1037025457"
print("TELEGRAM_BOT_TOKEN:", TELEGRAM_BOT_TOKEN)

# URL сайту
URL = "https://www.dar.gov.ua/news"

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    params = {"chat_id": CHAT_ID, "text": text}
    response = requests.get(url, params=params)
    print(f"Telegram API Response: {response.status_code} - {response.text}")

def check_news():
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
        target_date = datetime.datetime.now().strftime("%Y-%m-%d")

        found = False  # Прапорець для перевірки, чи була знайдена новина

        for date_element in dates:
            date = date_element.text.strip()
            print(f"Перевіряємо дату: {date}")

            # Якщо дата збігається з цільовою
            if date == target_date:
                send_telegram_message(f"🟢 Знайдено новину з датою {target_date}! Перевірте сайт: {URL}")
                print("Повідомлення надіслано.")
                found = True  # Позначаємо, що новина знайдена
                return  # Зупинити перевірку після першої знайденої новини

        # Якщо новина не знайдена
        if not found:
            print(f"Новин з датою {target_date} не знайдено.")
    except Exception as e:
        print("Помилка у виконанні запиту або парсингу:", e)

def send_status_message():
    send_telegram_message("✅ Скрипт працює!")

# Надіслати повідомлення при запуску
send_telegram_message("✅ Скрипт запущено і працює!")
# Одразу перевіряємо новини
check_news()

# Запуск перевірки новин кожні 30 хвилин
schedule.every(30).minutes.do(check_news)

# Надсилання повідомлення про статус о 8:00 та 17:00
schedule.every().day.at("08:00").do(send_status_message)
schedule.every().day.at("17:00").do(send_status_message)
# Надсилання тест
schedule.every().day.at("17:13").do(send_status_message)
schedule.every().day.at("18:00").do(send_status_message)
schedule.every().day.at("00:00").do(send_status_message)
while True:
    schedule.run_pending()
    time.sleep(1)
