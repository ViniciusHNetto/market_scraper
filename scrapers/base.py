from abc import ABC, abstractmethod
from typing import List, Optional
from models import RawProduct


class BaseMarketScraper(ABC):
    market_name: str

    @abstractmethod
    def search(self, query: str) -> List[RawProduct]:
        """Retorna candidatos. price pode vir None se precisar resolver depois."""
        raise NotImplementedError

    def resolve_price(self, product: RawProduct, quantity: int = 1) -> Optional[float]:
        return product.price