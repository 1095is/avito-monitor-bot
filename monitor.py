import os
import json
import requests
import xml.etree.ElementTree as ET

TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

FEED_URL = "https://avito2rss.duck.consulting/feeds/59424.atom"

SEEN_FILE = "seen.json"

ATOM = "{http://www.w3.org/2005/Atom}"


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


print("Проверяем Avito2RSS...")

response = requests.get(
    FEED_URL,
    timeout=30
)

response.raise_for_status()

root = ET.fromstring(response.content)

entries = root.findall(f"{ATOM}entry")

print(f"Найдено записей в ленте: {len(entries)}")

seen = load_seen()
new_items = []

for entry in entries:

    title = entry.findtext(
        f"{ATOM}title",
        "Без названия"
    )

    link_element = entry.find(
        f"{ATOM}link"
    )

    if link_element is not None:
        link = link_element.attrib.get(
            "href",
            ""
        )
    else:
        link = ""

    title = title.strip()
    link = link.strip()

    # Используем ссылку на объявление
    # как уникальный ID
    item_id = link

    # Если ссылки почему-то нет,
    # используем название
    if not item_id:
        item_id = title

    # Если это объявление уже было отправлено,
    # пропускаем его
    if item_id in seen:
        continue

    new_items.append(
        {
            "id": item_id,
            "title": title,
            "link": link
        }
    )


# --------------------------------------------------
# ПЕРВЫЙ ЗАПУСК
# --------------------------------------------------

if not seen:

    # Просто запоминаем уже существующие объявления.
    # Старые объявления НЕ отправляем.
    for item in new_items:
        seen.add(item["id"])

    save_seen(seen)

    send_telegram(
        "✅ Монитор Avito запущен!\n\n"
        f"В ленте найдено объявлений: {len(entries)}\n\n"
        "Существующие объявления запомнены.\n"
        "Теперь я буду присылать только новые."
    )

    print("Первый запуск. Существующие объявления запомнены.")


# --------------------------------------------------
# ОБЫЧНАЯ ПРОВЕРКА
# --------------------------------------------------

else:

    for item in new_items:

        message = (
            "🆕 Новое объявление на Avito!\n\n"
            f"{item['title']}\n\n"
            f"{item['link']}"
        )

        send_telegram(message)

        seen.add(item["id"])

        print(
            f"Отправлено новое объявление: "
            f"{item['title']}"
        )

    save_seen(seen)

    print(
        f"Новых объявлений отправлено: "
        f"{len(new_items)}"
    )
