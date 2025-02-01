import requests
from bs4 import BeautifulSoup
import schedule
import time
import datetime
import os
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

def send_telegram_message(text):
    print(f"[DEBUG] Надсилання повідомлення: {text}")
    for chat_id in CHAT_IDS:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        params = {"chat_id": chat_id, "text": text}
        response = requests.get(url, params=params)
        print(f"Message sent to {chat_id}. Response: {response.status_code} - {response.text}")

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


# Надіслати повідомлення при запуску
print("[DEBUG] Викликаємо `send_telegram_message` з текстом: Скрипт запущено і працює!")
send_telegram_message("✅ Скрипт запущено і працює!")
# Запустити перевірку
check_news()

# Запуск перевірки новин кожні 10 хвилин
schedule.every(10).minutes.do(check_news)

# Надсилання повідомлення про статус
schedule.every().day.at("08:00").do(lambda: send_telegram_message("✅ Скрипт працює!"))
schedule.every().day.at("17:00").do(lambda: send_telegram_message("✅ Скрипт працює!"))
schedule.every().day.at("23:25").do(lambda: send_telegram_message("✅ Скрипт працює!"))

while True:
    schedule.run_pending()
    time.sleep(10)
