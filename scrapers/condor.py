import time
import requests
from typing import List
from models import RawProduct
from scrapers.base import BaseMarketScraper
from config import REQUEST_TIMEOUT, REQUEST_DELAY_SECONDS
from urllib.parse import quote

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    ),
    "Accept": "application/json",
    "Origin": "https://www.condor.com.br",
    "Referer": "https://www.condor.com.br/",
}

# IDs fixos da loja usada (Wenceslau). Se precisar trocar de loja
# física no futuro, é só atualizar esses dois valores.
COMPANY_ID = 314
STORE_ID = 1433


class CondorScraper(BaseMarketScraper):
    market_name = "condor"

    def search(self, query: str) -> List[RawProduct]:
        url = f"https://sense.osuper.com.br/{COMPANY_ID}/{STORE_ID}/search"
        params = {
            "brands": "",
            "categories": "",
            "tags": "",
            "size": 12,
            "from": 0,
            "search": query,
            "sortField": "_score",
            "sortOrder": "desc",
        }

        response = requests.get(url, params=params, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        time.sleep(REQUEST_DELAY_SECONDS)

        if response.status_code != 200:
            print(f"[{self.market_name}] status {response.status_code} pra '{query}'")
            return []

        data = response.json()
        results = []
        for hit in data.get("hits", []):
            pricing = hit.get("pricing", {})
            price = pricing.get("promotionalPrice") or pricing.get("price")
            if price:
                search_url = f"https://www.condor.com.br/busca?search={quote(hit.get('name', ''))}"
                results.append(RawProduct(
                    name=hit.get("name", ""),
                    price=float(price),
                    url=search_url,
                ))
        return results