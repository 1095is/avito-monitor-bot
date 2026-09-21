import os
import time
import requests
from bs4 import BeautifulSoup

TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

AVITO_URL = "https://www.avito.ru/moskva/noutbuki?localPriority=0&q=%D0%BD%D0%BE%D1%83%D1%82%D0%B1%D1%83%D0%BA%D0%B8"


def send_telegram(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

    response = requests.post(
        url,
        data={
            "chat_id": CHAT_ID,
            "text": text
        },
        timeout=20
    )

    response.raise_for_status()


print("Запуск проверки Avito...")

try:
    response = requests.get(
        AVITO_URL,
        headers={
            "User-Agent": "Mozilla/5.0"
        },
        timeout=20
    )

    print("HTTP:", response.status_code)
    print("Размер страницы:", len(response.text))

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")

        title = soup.title.get_text(strip=True) if soup.title else "заголовок не найден"

        message = (
            "🔎 Avito отвечает.\n\n"
            f"HTTP: {response.status_code}\n"
            f"Размер страницы: {len(response.text)}\n"
            f"Заголовок: {title[:200]}"
        )

    elif response.status_code == 429:
        message = (
            "⚠️ Avito ограничил запрос.\n\n"
            "HTTP: 429 Too Many Requests\n\n"
            "Мы не будем обходить ограничение."
        )

    else:
        message = (
            f"⚠️ Avito вернул HTTP {response.status_code}."
        )

except Exception as e:
    message = (
        "❌ Ошибка при обращении к Avito.\n\n"
        f"{type(e).__name__}: {e}"
    )

send_telegram(message)
print(message)
