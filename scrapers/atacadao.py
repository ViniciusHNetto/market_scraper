from scrapers.vtex_generic import VtexScraper
from config import ATACADAO_POSTAL_CODE


class AtacadaoScraper(VtexScraper):
    def __init__(self):
        super().__init__(
            market_name="atacadao",
            base_url="https://www.atacadao.com.br",
            postal_code=ATACADAO_POSTAL_CODE,
        )