from scrapers.atacadao import AtacadaoScraper
from scrapers.condor import CondorScraper

# Registro central: pra adicionar um mercado novo no futuro, basta
# criar a classe (herdando de VtexScraper ou BaseMarketScraper) e
# registrar aqui.
SCRAPER_REGISTRY = {
    "atacadao": AtacadaoScraper,
    "condor": CondorScraper,
}