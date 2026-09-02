MARKETS = {
    "atacadao": "https://www.atacadao.com.br/",
    "condor": "https://www.condor.com.br/",
}

ITEMS = [
    "Suco Del Valle Manga 290ml",
    "Suco Del Valle Uva 290ml",
    "Suco Del Valle Pêssego 290ml",
    "Fanta Guaraná 350ml",
    "Fanta Laranja 350ml",
    "Sprite 350ml",
    "Sprite zero 350ml",
    "Coca 350ml",
    "Coca zero 350ml",
]

# Se True, usa a Anthropic API pra escolher o melhor match entre os
# resultados da busca. Se False, usa fuzzy matching simples (mais rápido
# e sem custo, mas menos esperto).
USE_LLM_MATCHER = False

REQUEST_TIMEOUT = 15
REQUEST_DELAY_SECONDS = 1.0  # educado com o servidor

# CEP usado pra resolver preços regionalizados no Atacadão.
# Troque pelo CEP de onde você quer comparar os preços.
ATACADAO_POSTAL_CODE = "80215-090"

# Quantidades simuladas pra detectar desconto progressivo (tipo "leve 6").
# 1 = preço avulso normal. Adicione outras se notar descontos em outras faixas.
BULK_QUANTITIES_TO_CHECK = [1, 6]

