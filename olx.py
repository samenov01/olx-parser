import re
import time
import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "ru-RU,ru;q=0.9",
}

SESSION = requests.Session()
SESSION.headers.update(HEADERS)


def fetch_listings(url: str) -> list[dict]:
    """Возвращает список объявлений с первой страницы."""
    try:
        resp = SESSION.get(url, timeout=15)
        resp.raise_for_status()
    except requests.RequestException as e:
        print(f"[ERROR] Не удалось получить страницу: {e}")
        return []

    soup = BeautifulSoup(resp.text, "html.parser")
    results = []

    # OLX рендерит данные в data-cy="l-card" или через JSON в <script>
    cards = soup.select("[data-cy='l-card']")
    if not cards:
        # Попытка через JSON в теге script
        results = _parse_json_data(soup)
        return results

    for card in cards:
        listing = _parse_card(card)
        if listing:
            results.append(listing)

    return results


def _parse_card(card) -> dict | None:
    try:
        link_tag = card.select_one("a[href]")
        if not link_tag:
            return None

        href = link_tag["href"]
        if not href.startswith("http"):
            href = "https://www.olx.kz" + href

        match = re.search(r"-ID(\w+)\.html", href)
        listing_id = match.group(1) if match else href.split("/")[-1]

        title_tag = card.select_one("h4, h6, [data-cy='ad-card-title']")
        title = title_tag.get_text(strip=True) if title_tag else "Без названия"

        price_tag = card.select_one("[data-testid='ad-price'], .price")
        price = price_tag.get_text(strip=True) if price_tag else "Цена не указана"

        # Дата публикации из текста карточки
        card_text = card.get_text(" ", strip=True)
        date_match = re.search(r"(\d{1,2}\s+\w+\s+\d{4}|[Сс]егодня|[Вв]чера)", card_text)
        posted_date = date_match.group(1).lower() if date_match else ""

        return {"id": listing_id, "title": title, "price": price, "url": href, "posted_date": posted_date}
    except Exception:
        return None


def _parse_json_data(soup) -> list[dict]:
    """Парсит данные из JSON внутри <script id='__NEXT_DATA__'>."""
    script = soup.find("script", {"id": "__NEXT_DATA__"})
    if not script:
        return []

    import json

    try:
        data = json.loads(script.string)
        ads = (
            data.get("props", {})
            .get("pageProps", {})
            .get("ads", [])
        )
        results = []
        for ad in ads:
            listing_id = str(ad.get("id", ""))
            title = ad.get("title", "Без названия")
            price_obj = ad.get("price", {})
            price = price_obj.get("displayValue", "Цена не указана") if price_obj else "Цена не указана"
            slug = ad.get("url", "")
            url = f"https://www.olx.kz{slug}" if slug.startswith("/") else slug
            if listing_id:
                results.append({"id": listing_id, "title": title, "price": price, "url": url})
        return results
    except Exception:
        return []


def get_phone(listing_id: str) -> str | None:
    """Пытается получить номер телефона через OLX API."""
    api_url = f"https://www.olx.kz/api/v1/offers/{listing_id}/limited-phones/"
    try:
        time.sleep(1)  # небольшая задержка чтобы не триггерить rate-limit
        resp = SESSION.get(api_url, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            phones = data.get("data", [])
            if phones:
                return phones[0].get("phone") or phones[0].get("number")
    except Exception:
        pass
    return None
