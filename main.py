from collections import defaultdict

from config import MARKETS, ITEMS, BULK_QUANTITIES_TO_CHECK
from scrapers.init import SCRAPER_REGISTRY
from matcher import rank_candidates
from price_utils import extract_pack_quantity, calculate_unit_price, strip_size
from models import PriceResult
from report import generate_html_report


def get_candidates(scraper, item: str):
    seen = set()
    all_candidates = []
    queries = {item}
    broad = strip_size(item)
    if broad and broad != item:
        queries.add(broad)

    for q in queries:
        for c in scraper.search(q):
            key = c.sku_id or c.name
            if key not in seen:
                seen.add(key)
                all_candidates.append(c)
    return all_candidates


def best_price_in_market(scraper, item: str):
    candidates = get_candidates(scraper, item)
    ranked = rank_candidates(item, candidates)

    best_result = None  # (candidate, unit_price_paid, pack_qty, purchase_qty, real_unit_price)
    for candidate in ranked:
        for qty in BULK_QUANTITIES_TO_CHECK:
            price = scraper.resolve_price(candidate, quantity=qty)
            if price is None:
                continue

            pack_qty = extract_pack_quantity(candidate.name)
            real_unit_price = calculate_unit_price(price, pack_qty)

            print(f"    candidato: {candidate.name} (comprando {qty}) -> "
                  f"R$ {price:.2f}/un (pack {pack_qty}) = R$ {real_unit_price:.2f}/un real")

            if best_result is None or real_unit_price < best_result[4]:
                best_result = (candidate, price, pack_qty, qty, real_unit_price)

    return best_result

def run():
    scrapers = {name: cls() for name, cls in SCRAPER_REGISTRY.items() if name in MARKETS}
    results: list[PriceResult] = []

    for item in ITEMS:
        for market_name, scraper in scrapers.items():
            print(f"Buscando '{item}' em {market_name}...")
            best = best_price_in_market(scraper, item)

            if best is None:
                print(f"  -> nenhum candidato com preço disponível em {market_name}")
                continue

            candidate, price, pack_qty, purchase_qty, unit_price = best
            result = PriceResult(
                market=market_name, query=item, matched_name=candidate.name,
                price=price, pack_quantity=pack_qty, purchase_quantity=purchase_qty,
                unit_price=unit_price, url=candidate.url,
            )
            results.append(result)
            print(f"  -> {result}")

    # agrupa os resultados por item (pra achar o mais barato de cada um)
    by_item = defaultdict(list)
    for r in results:
        by_item[r.query].append(r)

    # agrupa a escolha final por mercado (item 5 do pedido)
    by_market = defaultdict(list)
    for item in ITEMS:
        item_results = by_item.get(item)
        if not item_results:
            print(f"\nAVISO: '{item}' não encontrado em nenhum mercado")
            continue
        cheapest = min(item_results, key=lambda r: r.unit_price)
        by_market[cheapest.market].append((item, cheapest))

    print("\n=== ONDE COMPRAR CADA ITEM (agrupado por mercado) ===")
    for market in sorted(by_market.keys()):
        print(f"\n{market.upper()}:")
        for item, r in by_market[market]:
            print(f"  {item}: R$ {r.unit_price:.2f}/un - {r.matched_name}")
            if r.url:
                print(f"    {r.url}")
                
    generate_html_report(by_market)

    return results


if __name__ == "__main__":
    run()