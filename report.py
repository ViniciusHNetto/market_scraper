import os
from datetime import datetime


def generate_html_report(by_market: dict, output_path: str = "docs/index.html"):
    now = datetime.now().strftime("%d/%m/%Y %H:%M")
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
</style>
</head>
<body>
<h1>🛒 Comparador de Preços</h1>
<div class="updated">Atualizado em {now}</div>
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