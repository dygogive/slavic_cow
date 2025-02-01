from flask import Flask, request
import os
import requests


TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
BASE_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"
WEBHOOK_URL = f"https://slaviccow-production.up.railway.app/{TELEGRAM_BOT_TOKEN}"

def set_webhook():
    response = requests.post(f"{BASE_URL}/setWebhook", data={"url": WEBHOOK_URL})
    print(f"Webhook set: {response.status_code}, {response.json()}")

if __name__ == "__main__":
    set_webhook()


app = Flask(__name__)

# Токен Telegram бота
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

@app.route(f"/{TELEGRAM_BOT_TOKEN}", methods=["POST"])
def telegram_webhook():
    """Обробка вебхука Telegram."""
    update = request.get_json()

    if "message" in update:
        text = update["message"].get("text", "")
        if text == "/start":
            print("Команда /start отримана!")
    
    return "OK", 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
