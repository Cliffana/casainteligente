"""Amazon.es price scraper with historical tracking.

Usage:
    python scripts/scraper.py        # Scrape all products
    python scripts/scraper.py --id echo-dot-5  # Single product
"""

import os
import re
import json
import random
import datetime
import argparse
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
PRICES_FILE = DATA_DIR / "prices.json"

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:127.0) Gecko/20100101 Firefox/127.0",
]


def load_prices():
    if PRICES_FILE.exists():
        return json.loads(PRICES_FILE.read_text(encoding="utf-8"))
    return {"products": {}, "last_updated": None}


def save_prices(data):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    PRICES_FILE.write_text(
        json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8"
    )


def scrape_amazon_price(asin):
    url = f"https://www.amazon.es/dp/{asin}"
    headers = {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "pt-PT,pt;q=0.9,es;q=0.8,en;q=0.7",
        "Accept-Encoding": "gzip, deflate, br",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }
    try:
        resp = requests.get(url, headers=headers, timeout=20)
        resp.raise_for_status()
    except requests.RequestException as e:
        print(f"  [ERR] HTTP error for {asin}: {e}")
        return None

    text = resp.text

    # Method 1: JSON-LD structured data
    price = _extract_jsonld_price(text)
    if price is not None:
        return price

    # Method 2: priceblock element (old Amazon layout)
    price = _extract_regex_price(text, r'id="priceblock_ourprice"[^>]*>([^<]+)')
    if price is not None:
        return price

    # Method 3: a-price-whole (new Amazon layout)
    match = re.search(r'class="a-price-whole"[^>]*>(\d+)[^<]*<', text)
    if match:
        try:
            return float(match.group(1))
        except (ValueError, IndexError):
            pass

    # Method 4: corePriceDisplay
    match = re.search(
        r'a-price"[^>]*>[^<]*<span[^>]*aria-hidden="true">([\d.,]+)',
        text,
    )
    if match:
        try:
            return _parse_price_str(match.group(1))
        except (ValueError, IndexError):
            pass

    print(f"  [WARN] Could not extract price for ASIN {asin}")
    return None


def _extract_jsonld_price(html):
    for match in re.finditer(
        r'<script type="application/ld\+json">(.*?)</script>', html, re.DOTALL
    ):
        try:
            data = json.loads(match.group(1))
            items = data if isinstance(data, list) else [data]
            for item in items:
                if item.get("@type") in ("Product", "ItemPage"):
                    offers = item.get("offers", {})
                    if isinstance(offers, dict):
                        price = offers.get("price")
                        if price is not None:
                            return float(price)
                    elif isinstance(offers, list):
                        for offer in offers:
                            price = offer.get("price")
                            if price is not None:
                                return float(price)
        except (json.JSONDecodeError, KeyError, TypeError, ValueError):
            continue
    return None


def _extract_regex_price(html, pattern):
    match = re.search(pattern, html)
    if match:
        return _parse_price_str(match.group(1))
    return None


def _parse_price_str(s):
    s = s.strip().replace("EUR", "").replace("€", "").replace(" ", "").strip()
    s = s.replace(",", ".")
    s = re.sub(r"[^\d.]", "", s)
    if s:
        return float(s)
    return None


def get_product_id_by_asin(asin, prices_data):
    for pid, info in prices_data["products"].items():
        if info.get("asin") == asin:
            return pid
    return None


def scrape_all():
    prices_data = load_prices()
    today = datetime.date.today().isoformat()
    scraped = 0
    errors = 0

    print(f"[SCRAPER] Checking {len(prices_data['products'])} products...\n")

    for product_id, info in prices_data["products"].items():
        asin = info.get("asin", "")
        if not asin:
            continue

        # Skip if already scraped today
        history = info.get("history", [])
        if history and history[-1].get("date") == today:
            print(f"  [SKIP] {info['name']} — already updated today")
            continue

        print(f"  [>>] {info['name']} (ASIN: {asin})")
        price = scrape_amazon_price(asin)

        if price is not None:
            # Check for duplicate today
            if history and history[-1].get("date") == today:
                history[-1]["price"] = price
            else:
                history.append({"date": today, "price": price})
            print(f"  [OK]  {price:.2f} EUR")
            scraped += 1
        else:
            print(f"  [ERR] Failed to scrape")
            errors += 1

        # Be polite — delay between requests
        import time
        time.sleep(random.uniform(2.0, 4.0))

    prices_data["last_updated"] = today
    save_prices(prices_data)

    total = len(prices_data["products"])
    print(f"\n[DONE] Scraped: {scraped}/{total} | Errors: {errors}")
    return scraped


def scrape_single(product_id):
    prices_data = load_prices()
    if product_id not in prices_data["products"]:
        print(f"[ERR] Product '{product_id}' not found")
        return

    info = prices_data["products"][product_id]
    today = datetime.date.today().isoformat()
    asin = info.get("asin", "")

    print(f"  [>>] {info['name']} (ASIN: {asin})")
    price = scrape_amazon_price(asin)

    if price is not None:
        history = info.get("history", [])
        if history and history[-1].get("date") == today:
            history[-1]["price"] = price
        else:
            history.append({"date": today, "price": price})
        prices_data["last_updated"] = today
        save_prices(prices_data)
        print(f"  [OK]  {price:.2f} EUR")
    else:
        print(f"  [ERR] Failed to scrape")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Amazon.es Price Scraper")
    parser.add_argument("--id", help="Scrape a single product by ID")
    args = parser.parse_args()

    if args.id:
        scrape_single(args.id)
    else:
        scrape_all()
