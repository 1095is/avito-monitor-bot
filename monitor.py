import os
import urllib.request
import urllib.parse

TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

AVITO_URL = "https://www.avito.ru/moskva/noutbuki?localPriority=0&q=%D0%BD%D0%BE%D1%83%D1%82%D0%B1%D1%83%D0%BA%D0%B8"


def send_message(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

    data = urllib.parse.urlencode({
        "chat_id": CHAT_ID,
        "text": text
    }).encode("utf-8")

    request = urllib.request.Request(url, data=data)

    with urllib.request.urlopen(request, timeout=20) as response:
        print(response.read().decode("utf-8"))


print("Проверяем Avito...")

try:
    request = urllib.request.Request(
        AVITO_URL,
        headers={
            "User-Agent": "Mozilla/5.0"
        }
    )

    with urllib.request.urlopen(request, timeout=20) as response:
        status = response.status
        page = response.read().decode("utf-8", errors="ignore")

    message = (
        f"🔎 Avito доступен.\n"
        f"Код ответа: {status}\n"
        f"Размер страницы: {len(page)} символов"
    )

except Exception as e:
    message = (
        f"⚠️ Не удалось получить страницу Avito.\n\n"
        f"{type(e).__name__}: {e}"
    )

send_message(message)
print(message)
