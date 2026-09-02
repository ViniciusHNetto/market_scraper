from dataclasses import dataclass
from typing import Optional


@dataclass
class RawProduct:
    """Um resultado bruto de busca. price pode vir None se precisar
    ser resolvido depois (ex: lojas com preço regionalizado)."""
    name: str
    price: Optional[float] = None
    sku_id: Optional[str] = None
    url: Optional[str] = None
    ean: Optional[str] = None


@dataclass
class PriceResult:
    market: str
    query: str
    matched_name: str
    price: float
    pack_quantity: int
    purchase_quantity: int   # quantas unidades você precisa comprar pra pagar esse preço
    unit_price: float
    url: Optional[str] = None

    def __str__(self):
        pack_info = f" (pack de {self.pack_quantity})" if self.pack_quantity > 1 else ""
        qty_note = f" [compre {self.purchase_quantity}]" if self.purchase_quantity > 1 else ""
        return (f"[{self.market}] {self.matched_name}{pack_info}{qty_note} - "
                f"R$ {self.price:.2f} | unidade: R$ {self.unit_price:.2f}")

