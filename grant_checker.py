from flask import Flask, request

app = Flask(__name__)

@app.route("/")
def home():
    return "Бот працює!"

@app.route(f"/<TELEGRAM_BOT_TOKEN>", methods=["POST"])
def telegram_webhook():
    update = request.get_json()
    if "message" in update:
        text = update["message"].get("text", "")
        if text == "/start":
            print("Команда /start отримана!")
    return "OK", 200
