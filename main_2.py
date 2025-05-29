import csv
import json
from datetime import datetime
import time
import requests
from bs4 import BeautifulSoup

API_ALL_PRODUCT_URL = "https://api.korzinavdom.kz/client/showcases?page=0&size=10000&categoryNumber={category_id}"
API_PRODUCT_DETAILS_URL = "https://api.korzinavdom.kz/client/showcases/{product_id}"

with open('data.json', encoding="utf-8") as f:
    data = json.load(f)

def get_product_ids(category_id):
    url = API_ALL_PRODUCT_URL.format(category_id=category_id)
    results = []
    try:
        response = requests.get(url, timeout=10)
        result = response.json()
        items = result.get("data", {}).get("page", {}).get("content", [])

        for item in items:
            if "quantumNumber" in item:
                results.append(item["quantumNumber"])
        return results

    except Exception as e:
        print(f"Ошибка при получении списка товаров: {e}")
        return []



def get_product_desc(product_id):
    url = API_PRODUCT_DETAILS_URL.format(product_id=product_id)
    try:
        r = requests.get(url, timeout=10)
        if r.status_code != 200:
            return None
        item = r.json().get("data", {})
        return {
            "product_name": item.get("productName"),
            "price": item.get("productPrice", {}).get("current"),
            "article": item.get("vendorCode"),
            "parsed_at": datetime.now().isoformat()
        }
    except Exception as e:
        print(f"[Ошибка] Не удалось получить детали продукта {product_id}: {e}")
        return None


all_products = []

def collect_leaf_categories(node, result):
    if not node.get("isGroup"):
        result.append(node["number"])
    else:
        for child in node.get("children", []):
            collect_leaf_categories(child, result)

leaf_category_ids = []
for leaf_category in data["data"]["items"]:
    collect_leaf_categories(leaf_category, leaf_category_ids)


for category_id in leaf_category_ids:
    print(f"Обрабатываю категорию: {category_id}")
    product_ids = get_product_ids(category_id)
    print(f"Найдено товаров: {len(product_ids)}")
    for i, id in enumerate(product_ids):
        print(f"  [{i+1}/{len(product_ids)}] Товар ID: {id}")
        desc = get_product_desc(id)
        if desc:
            all_products.append(desc)
        time.sleep(0.1)  # защита от перегрузки

csv_filename = "products.csv"
with open(csv_filename, "w", encoding="utf-8", newline='') as f:
    writer = csv.DictWriter(f, fieldnames=["product_name", "price", "article", "parsed_at"])
    writer.writeheader()
    writer.writerows(all_products)