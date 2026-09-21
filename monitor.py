import os
import urllib.request
import urllib.parse

TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

AVITO_URL = "https://www.avito.ru/moskva/noutbuki?localPriority=0&q=%D0%BD%D0%BE%D1%83%D1%82%D0%B1%D1%83%D0%BA%D0%B8"

def send_message(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

    data = (
        f"chat_id={CHAT_ID}&"
        f"text={text}"
    ).encode("utf-8")

    request = urllib.request.Request(url, data=data)

    with urllib.request.urlopen(request) as response:
        print(response.read().decode())


print("Проверяем Avito...")
print(AVITO_URL)

send_message("🔎 Бот запущен и готов проверять Avito.")
