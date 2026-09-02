import time
import requests
from typing import List, Optional
from models import RawProduct
from scrapers.base import BaseMarketScraper
from config import REQUEST_TIMEOUT, REQUEST_DELAY_SECONDS

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    ),
    "Accept": "application/json",
    "Content-Type": "application/json",
}


class VtexScraper(BaseMarketScraper):
    """
    Scraper genérico pra lojas VTEX. Como preço/estoque geralmente é
    regionalizado, a busca (search) só serve pra achar candidatos
    (nome + SKU) — o preço real é resolvido depois, via simulação de
    checkout, só pro item que o matcher escolher.
    """

    def __init__(self, market_name: str, base_url: str, postal_code: str):
        self.market_name = market_name
        self.base_url = base_url.rstrip("/")
        self.postal_code = postal_code

    def search(self, query: str) -> List[RawProduct]:
        url = f"{self.base_url}/api/catalog_system/pub/products/search/"
        params = {"ft": query, "_from": 0, "_to": 49}  # pega até 50 resultados

        response = requests.get(url, params=params, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        time.sleep(REQUEST_DELAY_SECONDS)

        if response.status_code not in (200, 206):
            print(f"[{self.market_name}] status {response.status_code} pra '{query}'")
            return []

        try:
            data = response.json()
        except ValueError:
            print(f"[{self.market_name}] resposta não é JSON pra '{query}'")
            return []

        results = []
        for product in data:
            name = product.get("productName", "")
            product_url = product.get("link")
            for item in product.get("items", []):
                results.append(RawProduct(
                    name=item.get("nameComplete", name) or name,
                    price=None,
                    sku_id=item.get("itemId"),
                    ean=item.get("ean"),
                    url=product_url,
                ))
        return results

    def resolve_price(self, product: RawProduct, quantity: int = 1) -> Optional[float]:
        if not product.sku_id:
            return None

        url = f"{self.base_url}/api/checkout/pub/orderForms/simulation"
        body = {
            "items": [{"id": product.sku_id, "quantity": quantity, "seller": "1"}],
            "postalCode": self.postal_code,
            "country": "BRA",
        }

        try:
            response = requests.post(url, json=body, headers=HEADERS, timeout=REQUEST_TIMEOUT)
            time.sleep(REQUEST_DELAY_SECONDS)
            if response.status_code != 200:
                return None
            data = response.json()
        except (ValueError, requests.RequestException):
            return None

        items = data.get("items", [])
        if not items or items[0].get("availability") != "available":
            return None

        price_cents = items[0].get("price")
        if price_cents is None:
            return None
        return price_cents / 100  # já é o preço UNITÁRIO, com desconto de faixa aplicado




