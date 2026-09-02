from typing import List, Optional
from rapidfuzz import process, fuzz
from models import RawProduct
from price_utils import normalize, extract_size_token

DISTINGUISHING_WORDS = {
    "zero", "light",
    "alcoolica", "alcoolico",
    "fanta", "sprite", "guarana", "pepsi", "kuat", "schweppes", "antarctica",
    "manga", "uva", "pessego", "laranja", "limao", "maracuja", "abacaxi",
}

# Palavras que fazem parte do nome PADRÃO de certas marcas e não devem
# contar como "sabor diferente" na hora de filtrar candidatos.
# Ex: Sprite é sempre sabor limão — isso não é uma escolha, é o nome do produto.
BRAND_NAME_NOISE = {
    "sprite": {"limao"},
}


try:
    import anthropic
except ImportError:
    anthropic = None


def match_fuzzy(query: str, candidates: List[RawProduct]) -> Optional[RawProduct]:
    if not candidates:
        return None
    names = [c.name for c in candidates]
    best = process.extractOne(query, names, scorer=fuzz.token_sort_ratio)
    if best is None:
        return None
    best_name, score, idx = best
    if score < 60:  # threshold, ajuste conforme necessário
        return None
    return candidates[idx]


def match_with_llm(query: str, candidates: List[RawProduct]) -> Optional[RawProduct]:
    if not candidates:
        return None
    if anthropic is None:
        raise RuntimeError("pacote 'anthropic' não instalado")

    client = anthropic.Anthropic()  # usa ANTHROPIC_API_KEY do ambiente
    options_text = "\n".join(f"{i}: {c.name}" for i, c in enumerate(candidates))

    prompt = (
        f"Estou procurando exatamente este produto: \"{query}\".\n"
        f"Aqui estão os resultados de busca de um mercado:\n{options_text}\n\n"
        "Responda APENAS com o número (índice) do item que é EXATAMENTE o "
        "mesmo produto (mesma marca, sabor e tamanho/volume). "
        "Se nenhum bater exatamente, responda -1."
    )

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=10,
        messages=[{"role": "user", "content": prompt}],
    )
    text = response.content[0].text.strip()
    try:
        idx = int(text)
    except ValueError:
        return None
    if idx < 0 or idx >= len(candidates):
        return None
    return candidates[idx]


def find_best_match(query: str, candidates: List[RawProduct], use_llm: bool = False):
    if use_llm:
        return match_with_llm(query, candidates)
    return match_fuzzy(query, candidates)


def rank_fuzzy(query: str, candidates: List[RawProduct], limit: int = 15, threshold: int = 55):
    if not candidates:
        return []
    names = [c.name for c in candidates]
    matches = process.extract(query, names, scorer=fuzz.token_sort_ratio, limit=limit)
    return [candidates[idx] for _, score, idx in matches if score >= threshold]


def match_by_tokens(query: str, candidates: List[RawProduct]) -> List[RawProduct]:
    q_tokens = normalize(query).split()
    q_word_set = set(q_tokens)
    brand = q_tokens[0] if q_tokens else ""
    ignore_words = BRAND_NAME_NOISE.get(brand, set())

    matches = []
    for c in candidates:
        c_norm = normalize(c.name)
        c_words = set(c_norm.split()) - ignore_words

        if not all(tok in c_norm for tok in q_tokens):
            continue
        if DISTINGUISHING_WORDS & c_words - q_word_set:
            continue
        matches.append(c)
    return matches


def rank_candidates(query: str, candidates: List[RawProduct]) -> List[RawProduct]:
    """Estratégia principal: containment por token. Se não achar nada
    (ex: erro de digitação), cai pra fuzzy como rede de segurança."""
    exact = match_by_tokens(query, candidates)
    if exact:
        return exact
    return match_fuzzy_multi(query, candidates)


def match_fuzzy_multi(query: str, candidates: List[RawProduct], limit: int = 10, threshold: int = 40):
    if not candidates:
        return []
    q_norm = normalize(query)
    q_tokens = q_norm.split()
    brand_token = q_tokens[0] if q_tokens else ""
    size_token = extract_size_token(query)
    required_distinguishing = DISTINGUISHING_WORDS & set(q_tokens)  # ex: {"pessego"}

    names = [c.name for c in candidates]
    raw_matches = process.extract(query, names, scorer=fuzz.token_set_ratio, limit=limit * 3)

    filtered = []
    for name, score, idx in raw_matches:
        if score < threshold:
            continue
        c_norm = normalize(name)
        if brand_token and brand_token not in c_norm:
            continue
        if size_token and size_token not in c_norm.replace(" ", ""):
            continue
        if not required_distinguishing.issubset(set(c_norm.split())):
            continue
        filtered.append(candidates[idx])
        if len(filtered) >= limit:
            break
    return filtered


