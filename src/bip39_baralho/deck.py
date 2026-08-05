"""Representação do baralho de 52 cartas e conversão para índices 0-51."""

from __future__ import annotations

SUITS = [("Paus", "♣", "C"), ("Ouros", "♦", "D"), ("Copas", "♥", "H"), ("Espadas", "♠", "S")]
VALUES = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]

_VALUE_ALIASES = {"T": "10", "10": "10"}

_SUIT_BY_LETTER = {letter: i for i, (_, _, letter) in enumerate(SUITS)}
_SUIT_BY_SYMBOL = {symbol: i for i, (_, symbol, _) in enumerate(SUITS)}
_SUIT_BY_NAME = {name.upper(): i for i, (name, _, _) in enumerate(SUITS)}


def card_code(index: int) -> str:
    """Índice 0-51 -> código curto, ex.: 0 -> 'A♣', 51 -> 'K♠'."""
    _validate_index(index)
    v = VALUES[index % 13]
    _, symbol, _ = SUITS[index // 13]
    return f"{v}{symbol}"


def card_name(index: int) -> str:
    """Índice 0-51 -> nome por extenso, ex.: 0 -> 'A de Paus'."""
    _validate_index(index)
    v = VALUES[index % 13]
    name, _, _ = SUITS[index // 13]
    return f"{v} de {name}"


def parse_card(text: str) -> int:
    """Converte uma notação de carta (ex.: 'AC', 'A♣', '10-Copas', 'KS') no índice 0-51.

    Aceita símbolo de naipe (♣ ♦ ♥ ♠), letra (C D H S) ou nome em português
    (Paus, Ouros, Copas, Espadas), e valor A/2-10/J/Q/K (T também é aceito como 10).
    """
    raw = text.strip().upper().replace(" ", "").replace("-", "").replace("DE", "")
    if not raw:
        raise ValueError(f"carta vazia: {text!r}")

    suit_idx = None
    for symbol, idx in _SUIT_BY_SYMBOL.items():
        if raw.endswith(symbol):
            suit_idx = idx
            raw = raw[: -len(symbol)]
            break
    if suit_idx is None:
        for name, idx in _SUIT_BY_NAME.items():
            if raw.endswith(name):
                suit_idx = idx
                raw = raw[: -len(name)]
                break
    if suit_idx is None:
        for letter, idx in _SUIT_BY_LETTER.items():
            if raw.endswith(letter):
                suit_idx = idx
                raw = raw[: -len(letter)]
                break
    if suit_idx is None:
        raise ValueError(f"naipe não reconhecido em {text!r}")

    value = _VALUE_ALIASES.get(raw, raw)
    if value not in VALUES:
        raise ValueError(f"valor não reconhecido em {text!r}: {raw!r}")

    return suit_idx * 13 + VALUES.index(value)


def full_deck() -> list[int]:
    """Retorna os 52 índices de carta, em ordem (0..51)."""
    return list(range(52))


def _validate_index(index: int) -> None:
    if not (0 <= index <= 51):
        raise ValueError(f"índice de carta fora do intervalo 0-51: {index}")
