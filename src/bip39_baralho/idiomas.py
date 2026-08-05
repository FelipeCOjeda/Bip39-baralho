"""Idiomas suportados (todas as wordlists oficiais do BIP-0039, cada uma com
exatamente 2048 palavras — a mesma regra matemática do baralho vale para
qualquer uma delas, só a lista de palavras muda)."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"

IDIOMAS = {
    "english": "bip39-english.txt",
    "portuguese": "bip39-portuguese.txt",
    "spanish": "bip39-spanish.txt",
    "french": "bip39-french.txt",
    "italian": "bip39-italian.txt",
    "czech": "bip39-czech.txt",
    "japanese": "bip39-japanese.txt",
    "korean": "bip39-korean.txt",
    "chinese_simplified": "bip39-chinese_simplified.txt",
    "chinese_traditional": "bip39-chinese_traditional.txt",
}

PADRAO = "english"


@lru_cache(maxsize=None)
def carregar_wordlist(idioma: str = PADRAO) -> tuple[str, ...]:
    if idioma not in IDIOMAS:
        disponiveis = ", ".join(sorted(IDIOMAS))
        raise ValueError(f"idioma desconhecido: {idioma!r}. Disponíveis: {disponiveis}")
    caminho = DATA_DIR / IDIOMAS[idioma]
    if not caminho.exists():
        raise FileNotFoundError(f"arquivo de wordlist não encontrado: {caminho}")
    palavras = caminho.read_text(encoding="utf-8").split()
    if len(palavras) != 2048:
        raise ValueError(
            f"wordlist '{idioma}' com tamanho inesperado: {len(palavras)} (esperado 2048)"
        )
    return tuple(palavras)
