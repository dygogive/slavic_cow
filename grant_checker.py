def handle_commands():
    """Функція для обробки команд із Telegram."""
    global is_bot_running

    last_update_id = None  # Змінна для збереження останнього обробленого update_id
    while True:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getUpdates"
        params = {"offset": last_update_id, "timeout": 10}
        response = requests.get(url, params=params)
        updates = response.json()["result"]

        for update in updates:
            # Оновити останній оброблений update_id
            last_update_id = update["update_id"] + 1
            if "message" in update:
                chat_id = str(update["message"]["chat"]["id"])
                text = update["message"].get("text", "")

                # Обробляємо лише команди від дозволених чатів
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
