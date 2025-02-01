from flask import Flask, request
import os

app = Flask(__name__)

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

@app.route("/")
def home():
    return "Бот працює!"

@app.route(f"/{TELEGRAM_BOT_TOKEN}", methods=["POST"])
def telegram_webhook():
    update = request.get_json()
    if "message" in update:
        text = update["message"].get("text", "")
        if text == "/start":
            print("Команда /start отримана!")
    return "OK", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
