import re
import unicodedata

SIZE_PATTERN = re.compile(r'\s*\d+\s*(ml|l|g|kg)\b', re.IGNORECASE)
SIZE_TOKEN_PATTERN = re.compile(r'\d+\s*(?:ml|l|g|kg)\b')

def extract_size_token(text: str) -> str:
    match = SIZE_TOKEN_PATTERN.search(normalize(text))
    return match.group(0).replace(" ", "") if match else ""


def normalize(text: str) -> str:
    text = text.lower()
    text = unicodedata.normalize('NFKD', text)
    text = ''.join(c for c in text if not unicodedata.combining(c))
    text = re.sub(r'[-,/]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    text = re.sub(r'\bsem\s+acucar\b', 'zero', text)  # sinônimo
    text = re.sub(r'\bdiet\b', 'zero', text)           # sinônimo
    return text


def strip_size(text: str) -> str:
    """Remove o volume/peso do texto pra ampliar a busca.
    Ex: 'Coca 350ml' -> 'Coca'"""
    return SIZE_PATTERN.sub('', text).strip()

# Padrões comuns em nomes de produtos de mercado BR pra indicar pack.
# Ex: "C/6", "6X350ML", "PACK 6", "LEVE 6", "KIT 6 UNIDADES", "6 UN"
PACK_PATTERNS = [
    r"c/\s*(\d+)",
    r"\b(\d+)\s*x\s*\d+\s*(?:ml|l|g|kg)\b",  # "6x350ml", "8x350ml" etc
    r"pack\s*(?:com|c/)?\s*(\d+)",
    r"kit\s*(?:com|c/)?\s*(\d+)",
    r"leve\s*(\d+)",
    r"(\d+)\s*un(?:id(?:ades)?)?\b",
]


def extract_pack_quantity(product_name: str) -> int:
    """Tenta descobrir quantas unidades vêm no produto. Retorna 1 se não achar nada."""
    name_lower = product_name.lower()
    for pattern in PACK_PATTERNS:
        match = re.search(pattern, name_lower)
        if match:
            qty = int(match.group(1))
            if 1 < qty <= 100:  # sanity check, evita capturar "350ml" como pack de 350
                return qty
    return 1


def calculate_unit_price(price: float, pack_quantity: int) -> float:
    if pack_quantity <= 0:
        pack_quantity = 1
    return round(price / pack_quantity, 4)