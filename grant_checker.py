import requests
from bs4 import BeautifulSoup
import schedule
import time
import datetime
import os
from pytz import timezone

# === Налаштування ===
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_IDS = ["8348118669"]
KYIV_TZ = timezone("Europe/Kiev")

URL = "https://dar.gov.ua/novyny"

# Ключові слова — головне що новина про корів
KEYWORDS = [
    "корів",
    "корови",
    "корова",
]

# Ключові слова що означають ЗУПИНКУ — ігноруємо
STOP_KEYWORDS = [
    "призупинено",
    "завершено",
    "зупинено",
]

SENT_FILE = "sent_links.txt"

# === Функції ===

def load_sent_links():
    if not os.path.exists(SENT_FILE):
        return set()
    with open(SENT_FILE, "r") as f:
        return set(line.strip() for line in f.readlines())

def save_sent_link(link):
    with open(SENT_FILE, "a") as f:
        f.write(link + "\n")

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    for chat_id in CHAT_IDS:
        params = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
        try:
            response = requests.get(url, params=params, timeout=10)
            print(f"Надіслано до {chat_id}: {response.status_code}")
        except Exception as e:
            print(f"Помилка надсилання до {chat_id}: {e}")

def parse_date(text):
    """Парсить дату формату DD.MM.YYYY з тексту"""
    for word in text.split():
        try:
            return datetime.datetime.strptime(word.strip(), "%d.%m.%Y").date()
        except:
            continue
    return None

def check_site():
    try:
        response = requests.get(URL, timeout=15)
        soup = BeautifulSoup(response.text, "html.parser")
        sent_links = load_sent_links()

        now = datetime.datetime.now(KYIV_TZ)
        today = now.date()

        cards = soup.find_all(["article", "div", "li"])

        for card in cards:
            all_text = card.get_text(separator=" ")

            # Шукаємо дату в картці
            news_date = parse_date(all_text)

            # Якщо дата не знайдена або новина стара — пропускаємо
            if news_date is None or news_date < today:
                continue

            # Шукаємо посилання в картці
            link = card.find("a", href=True)
            if not link:
                continue

            title = link.get_text(strip=True).lower()
            href = link["href"]

            if not title or len(title) < 10:
                continue

            # Пропускаємо новини про зупинку
            if any(kw in title for kw in STOP_KEYWORDS):
                print(f"Пропускаємо (зупинка): {title}")
                continue

            # Головна умова — є слово про корів
            if any(kw in title for kw in KEYWORDS):
                full_url = href if href.startswith("http") else "https://dar.gov.ua" + href

                if full_url not in sent_links:
                    msg = (
                        f"🐄 <b>УВАГА! Нова новина про корів!</b>\n\n"
                        f"📅 Дата: {news_date.strftime('%d.%m.%Y')}\n"
                        f"📌 {link.get_text(strip=True)}\n\n"
                        f"🔗 {full_url}\n\n"
                        f"⏰ {now.strftime('%d.%m.%Y %H:%M')}\n\n"
                        f"👉 Перевір та подавай заявку!"
                    )
                    send_telegram_message(msg)
                    save_sent_link(full_url)
                    print(f"✅ Знайдено: {full_url} (дата: {news_date})")

        print(f"[{now.strftime('%H:%M')}] Перевірено. Сьогодні: {today.strftime('%d.%m.%Y')}")

    except Exception as e:
        print(f"Помилка: {e}")

def send_status_message():
    now = datetime.datetime.now(KYIV_TZ).strftime("%d.%m.%Y %H:%M")
    send_telegram_message(f"✅ Бот активний. Моніторинг dar.gov.ua/novyny\n⏰ {now}")

# === Запуск ===
send_status_message()
check_site()

schedule.every(20).minutes.do(check_site)      # кожні 20 хвилин
schedule.every().day.at("08:00").do(send_status_message)
schedule.every().day.at("20:00").do(send_status_message)

while True:
    schedule.run_pending()
    time.sleep(60)