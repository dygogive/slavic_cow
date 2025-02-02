import requests
from bs4 import BeautifulSoup
import schedule
import time
import datetime
import os
from pytz import timezone

isCheck = False

# Токен і Chat ID для Telegram
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Список ID чатів
CHAT_ID_1 = "1037025457"
CHAT_ID_2 = "8171469284"

# URL сайту
URL = "https://www.dar.gov.ua/news"

# Часовий пояс Києва
KYIV_TZ = timezone("Europe/Kiev")


def send_telegram_message(text):
    # Додаємо унікальний ID до повідомлення
    unique_text = f"{text} | ID: {datetime.datetime.now().timestamp()}"
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    # Перший чат
    params1 = {"chat_id": CHAT_ID_1, "text": unique_text}
    response1 = requests.get(url, params=params1)
    print(f"Message sent to {CHAT_ID_1}. Response: {response1.status_code} - {response1.text}")
    # Другий чат
    params2 = {"chat_id": CHAT_ID_2, "text": unique_text}
    response2 = requests.get(url, params=params2)
    print(f"Message sent to {CHAT_ID_2}. Response: {response2.status_code} - {response2.text}")
    

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
            if isCheck:
                send_telegram_message(f"🔴 Новин з датою {target_date} не знайдено.")
    except Exception as e:
        print("Помилка у виконанні запиту або парсингу:", e)


# Надіслати повідомлення при запуску
print("[DEBUG] Викликаємо `send_telegram_message` з текстом: Скрипт запущено і працює!")
send_telegram_message(f"✅ Скрипт запущено і працює!")
# Запустити перевірку
check_news()

# Запуск перевірки новин кожні 10 хвилин
schedule.every(10).minutes.do(check_news)

def check_program():
    global isCheck  # Вказуємо, що змінюємо глобальну змінну
    isCheck = True
    check_news()
    isCheck = False


# Надсилання повідомлення про статус
schedule.every().day.at("08:00").do(check_program)
schedule.every().day.at("01:04").do(check_program)

while True:
    schedule.run_pending()
    time.sleep(1)
