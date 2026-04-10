import requests
from bs4 import BeautifulSoup
import datetime

URL = "https://dar.gov.ua/novyny"

KEYWORDS = ["корів", "корови", "корова"]
STOP_KEYWORDS = ["призупинено", "завершено", "зупинено"]

def parse_date(text):
    for word in text.split():
        try:
            return datetime.datetime.strptime(word.strip(), "%d.%m.%Y").date()
        except:
            continue
    return None

def test_check():
    print(f"Завантажую {URL} ...\n")
    response = requests.get(URL, timeout=15)
    soup = BeautifulSoup(response.text, "html.parser")

    today = datetime.date.today()
    print(f"Сьогодні: {today.strftime('%d.%m.%Y')}\n")
    print("=" * 50)

    cards = soup.find_all(["article", "div", "li"])
    print(f"Знайдено карток на сторінці: {len(cards)}\n")

    found_any = False

    for card in cards:
        all_text = card.get_text(separator=" ")
        news_date = parse_date(all_text)

        if news_date is None:
            continue

        link = card.find("a", href=True)
        if not link:
            continue

        title = link.get_text(strip=True).lower()
        if not title or len(title) < 10:
            continue

        # Показуємо ВСІ новини з датою (для діагностики)
        print(f"📰 Дата: {news_date} | Заголовок: {title[:60]}")

        if news_date < today:
            print(f"   ⏩ Стара новина — пропускаємо\n")
            continue

        if any(kw in title for kw in STOP_KEYWORDS):
            print(f"   🔴 Зупинка — пропускаємо\n")
            continue

        if any(kw in title for kw in KEYWORDS):
            print(f"   🐄 ЗНАЙДЕНО НОВИНУ ПРО КОРІВ! ✅\n")
            found_any = True
        else:
            print(f"   ⚪ Нова, але не про корів\n")

    print("=" * 50)
    if found_any:
        print("✅ Бот би надіслав повідомлення!")
    else:
        print("❌ Новин про корів сьогодні не знайдено (це нормально якщо їх немає)")

test_check()
