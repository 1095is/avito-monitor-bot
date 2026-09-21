import os
import urllib.parse
import urllib.request

token = os.environ["TELEGRAM_BOT_TOKEN"]
chat_id = os.environ["TELEGRAM_CHAT_ID"]

message = "🎉 Работает! Твой Avito-бот успешно подключён к Telegram."

url = f"https://api.telegram.org/bot{token}/sendMessage"

data = urllib.parse.urlencode({
    "chat_id": chat_id,
    "text": message
}).encode()

request = urllib.request.Request(url, data=data)

with urllib.request.urlopen(request) as response:
    print(response.read().decode())
