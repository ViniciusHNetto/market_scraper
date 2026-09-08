import os
from datetime import datetime
from zoneinfo import ZoneInfo


def build_comparison_table(items: list, markets: list, by_item: dict) -> str:
    rows = ['<table class="comparison"><thead><tr><th>Item</th>']
    for market in markets:
        rows.append(f"<th>{market}</th>")
    rows.append("</tr></thead><tbody>")

    for item in items:
        item_results = by_item.get(item, [])
        prices_by_market = {r.market: r.unit_price for r in item_results}
        cheapest_price = min(prices_by_market.values()) if prices_by_market else None

        rows.append(f"<tr><td class='item-col'>{item}</td>")
        for market in markets:
            price = prices_by_market.get(market)
            if price is None:
                rows.append("<td class='na'>—</td>")
            else:
                cls = "cheapest" if price == cheapest_price else ""
                rows.append(f"<td class='{cls}'>R$ {price:.2f}</td>")
        rows.append("</tr>")

    rows.append("</tbody></table>")
    return "".join(rows)


def generate_html_report(by_market: dict, items: list, markets: list, by_item: dict,
                          output_path: str = "docs/index.html"):
    now = datetime.now(ZoneInfo("America/Sao_Paulo")).strftime("%d/%m/%Y %H:%M")
    table_html = build_comparison_table(items, markets, by_item)

    html = [f"""<!DOCTYPE html>
<html lang="pt-br">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Comparador de Preços</title>
<style>
  body {{ font-family: -apple-system, system-ui, sans-serif; max-width: 480px;
          margin: 0 auto; padding: 16px; background: #f5f5f5; color: #222; }}
  h1 {{ font-size: 20px; margin-bottom: 4px; }}
  h3 {{ font-size: 15px; margin: 24px 0 8px; }}
  .updated {{ color: #777; font-size: 13px; margin-bottom: 20px; }}
  .market {{ background: white; border-radius: 12px; padding: 12px 16px;
             margin-bottom: 16px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
  .market h2 {{ font-size: 16px; margin: 0 0 4px; text-transform: capitalize; }}
  .item {{ padding: 10px 0; border-top: 1px solid #eee; }}
  .item:first-of-type {{ border-top: none; }}
  .item-name {{ font-weight: 600; font-size: 14px; }}
  .item-price {{ color: #1a7f37; font-weight: 700; font-size: 14px; }}
  .item-detail {{ font-size: 12px; color: #777; margin-top: 2px; }}
  a {{ color: #0366d6; text-decoration: none; font-size: 12px; }}

  table.comparison {{ width: 100%; border-collapse: collapse; background: white;
                       border-radius: 12px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                       font-size: 12px; margin-bottom: 8px; }}
  table.comparison th, table.comparison td {{ padding: 8px 6px; text-align: center;
                                               border-bottom: 1px solid #eee; }}
  table.comparison th {{ background: #fafafa; text-transform: capitalize; font-size: 11px; }}
  table.comparison .item-col {{ text-align: left; font-weight: 600; }}
  table.comparison .cheapest {{ background: #e6f4ea; color: #1a7f37; font-weight: 700; }}
  table.comparison .na {{ color: #ccc; }}
</style>
</head>
<body>
<h1>🛒 Comparador de Preços</h1>
<div class="updated">Atualizado em {now}</div>

<h3>Comparativo por mercado</h3>
{table_html}
"""]

    for market in sorted(by_market.keys()):
        html.append(f'<div class="market"><h2>{market}</h2>')
        for item, r in by_market[market]:
            qty_note = f" (compre {r.purchase_quantity})" if r.purchase_quantity > 1 else ""
            link = f'<a href="{r.url}" target="_blank">Ver produto →</a>' if r.url else ""
            html.append(f"""
            <div class="item">
              <div class="item-name">{item}</div>
              <div class="item-price">R$ {r.unit_price:.2f}/un{qty_note}</div>
              <div class="item-detail">{r.matched_name}</div>
              {link}
            </div>""")
        html.append("</div>")

    html.append("</body></html>")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(html))
    print(f"Relatório salvo em {output_path}")
