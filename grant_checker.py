import requests
from bs4 import BeautifulSoup
import datetime
import re

URL = "https://www.dar.gov.ua/novyny/"
KEYWORD = "корів"
DATE_LIMIT = datetime.datetime.strptime("01.04.2026", "%d.%m.%Y").date()

# ===== Telegram =====
BOT_TOKEN = "YOUR_BOT_TOKEN"
CHAT_ID = "YOUR_CHAT_ID"


def send_telegram_message(text: str):
    api_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text
    }
    response = requests.post(api_url, data=payload, timeout=15)
    response.raise_for_status()


def parse_date(text: str):
    match = re.search(r"\b\d{2}\.\d{2}\.\d{4}\b", text)
    if not match:
        return None
    return datetime.datetime.strptime(match.group(0), "%d.%m.%Y").date()


def normalize_text(text: str) -> str:
    return " ".join(text.split()).strip()


def check_news():
    response = requests.get(URL, timeout=15)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    found_news = []

    # На сторінці кожна новина йде як h3 з посиланням, а далі поруч дата.
    # Беремо всі заголовки новин.
    headings = soup.find_all(["h3", "h2", "h4"])

    for heading in headings:
        link = heading.find("a", href=True)
        if not link:
            continue

        title = normalize_text(link.get_text(" ", strip=True))
        if not title:
            continue

        title_lower = title.lower()

        # Шукаємо саме слово "корів" у заголовку
        if KEYWORD not in title_lower:
            continue

        # Шукаємо дату поруч після заголовка
        date_found = None

        # 1) спроба: взяти текст наступних сусідів
        for sibling in heading.next_siblings:
            if isinstance(sibling, str):
                sibling_text = sibling.strip()
            else:
                sibling_text = normalize_text(sibling.get_text(" ", strip=True))

            if not sibling_text:
                continue

            date_found = parse_date(sibling_text)
            if date_found:
                break

            # якщо натрапили на наступний заголовок, зупиняємось
            if getattr(sibling, "name", None) in ["h2", "h3", "h4"]:
                break

        # 2) запасний варіант: взяти трохи тексту з батьківського блоку
        if date_found is None:
            parent_text = normalize_text(heading.parent.get_text(" ", strip=True))
            date_found = parse_date(parent_text)

        if date_found is None:
            continue

        if date_found > DATE_LIMIT:
            href = link["href"]
            if href.startswith("/"):
                href = "https://www.dar.gov.ua" + href

            found_news.append({
                "title": title,
                "date": date_found,
                "url": href
            })

    return found_news


def main():
    try:
        news_list = check_news()

        if news_list:
            messages = []
            for item in news_list:
                messages.append(
                    f"Знайдено новину про корів:\n"
                    f"Заголовок: {item['title']}\n"
                    f"Дата: {item['date'].strftime('%d.%m.%Y')}\n"
                    f"Посилання: {item['url']}"
                )

            final_message = "\n\n".join(messages)
            print(final_message)
            send_telegram_message(final_message)
        else:
            print("Новин зі словом 'корів' і датою новішою за 01.04.2026 не знайдено.")

    except Exception as e:
        error_text = f"Помилка бота: {e}"
        print(error_text)
        # за бажанням можна і помилку слати в Telegram
        # send_telegram_message(error_text)


if __name__ == "__main__":
    main()