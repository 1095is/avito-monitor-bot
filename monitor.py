import os
import json
import requests

from playwright.sync_api import sync_playwright


TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

AVITO_URL = (
    "https://www.avito.ru/moskva/noutbuki"
    "?localPriority=0"
    "&q=%D0%BD%D0%BE%D1%83%D1%82%D0%B1%D1%83%D0%BA%D0%B8"
)

SEEN_FILE = "seen.json"


def send_telegram(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

    response = requests.post(
        url,
        data={
            "chat_id": CHAT_ID,
            "text": text,
            "disable_web_page_preview": False
        },
        timeout=20
    )

    response.raise_for_status()


def load_seen():
    if not os.path.exists(SEEN_FILE):
        return set()

    try:
        with open(SEEN_FILE, "r", encoding="utf-8") as file:
            return set(json.load(file))
    except Exception:
        return set()


def save_seen(seen):
    with open(SEEN_FILE, "w", encoding="utf-8") as file:
        json.dump(
            list(seen),
            file,
            ensure_ascii=False,
            indent=2
        )


print("Открываем Avito через браузер...")

with sync_playwright() as p:

    browser = p.chromium.launch(
        headless=True
    )

    page = browser.new_page(
        viewport={
            "width": 1280,
            "height": 900
        }
    )

    page.goto(
        AVITO_URL,
        wait_until="domcontentloaded",
        timeout=60000
    )

    page.wait_for_timeout(5000)

    print("Страница открыта.")
    print("Заголовок:", page.title())

    body_text = page.locator("body").inner_text()

    print("Размер страницы:", len(body_text))

    # Проверяем, не показал ли Avito проверку
    blocked_words = [
        "captcha",
        "капча",
        "проверка",
        "робот",
        "robot"
    ]

    body_lower = body_text.lower()

    for word in blocked_words:
        if word in body_lower:
            print(
                f"⚠️ Обнаружена возможная проверка Avito: {word}"
            )

    # Сохраняем первые 3000 символов страницы
    # в лог GitHub Actions
    print("\n--- НАЧАЛО ТЕКСТА СТРАНИЦЫ ---")
    print(body_text[:3000])
    print("--- КОНЕЦ ТЕКСТА ---\n")

    # Ищем ссылки на объявления Avito
    links = page.locator("a").all()

    items = []

    for link_element in links:

        try:
            href = link_element.get_attribute("href")
            title = link_element.inner_text().strip()
        except Exception:
            continue

        if not href:
            continue

        if "/moskva/noutbuki/" not in href:
            continue

        if not title:
            continue

        if href.startswith("/"):
            href = "https://www.avito.ru" + href

        items.append(
            {
                "id": href,
                "title": title,
                "link": href
            }
        )

    browser.close()


# Убираем дубликаты
unique_items = {}

for item in items:
    unique_items[item["id"]] = item

items = list(unique_items.values())

print(f"Найдено объявлений на странице: {len(items)}")

seen = load_seen()

# Первый запуск
if not seen:

    for item in items:
        seen.add(item["id"])

    save_seen(seen)

    send_telegram(
        "✅ Монитор Avito запущен через браузер!\n\n"
        f"На странице найдено объявлений: {len(items)}\n\n"
        "Существующие объявления запомнены.\n"
        "Теперь буду присылать только новые."
    )

    print("Первый запуск завершён.")

else:

    new_items = []

    for item in items:

        if item["id"] not in seen:
            new_items.append(item)

    print(
        f"Новых объявлений: {len(new_items)}"
    )

    for item in new_items:

        message = (
            "🆕 Новое объявление на Avito!\n\n"
            f"{item['title']}\n\n"
            f"{item['link']}"
        )

        send_telegram(message)

        seen.add(item["id"])

    save_seen(seen)

    print("Проверка завершена.")
