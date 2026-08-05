"""Regra matemática que converte duas cartas (retiradas sem reposição) em uma
palavra BIP39, replicando exatamente a planilha `tabela_baralho_bip39.xlsx`
(que usa a wordlist em inglês, mas a mesma regra vale para qualquer um dos
10 idiomas oficiais do BIP-0039 — veja `idiomas.py`):

    a  = índice da 1ª carta (0-51)
    b  = índice da 2ª carta (0-51, b != a)
    b' = b se b < a, senão b - 1        (índice ajustado, 0-50)
    N  = 51*a + b'                       (0-2651)

    N em 0..2047   -> combinação válida, palavra = wordlist[N]
    N em 2048..2651 -> combinação descartada (devolver as cartas e repetir)
"""

from __future__ import annotations

from dataclasses import dataclass

from . import deck
from .idiomas import IDIOMAS, PADRAO, carregar_wordlist

VALID_MAX = 2047
DISCARD_MIN = 2048
DISCARD_MAX = 2651

# Mantido por compatibilidade: wordlist em inglês (idioma padrão da planilha original).
WORDLIST = carregar_wordlist(PADRAO)


@dataclass(frozen=True)
class Resultado:
    a: int
    b: int
    b_ajustado: int
    n: int
    valido: bool
    palavra: str | None
    idioma: str = PADRAO

    @property
    def padrao(self) -> str:
        return f"{deck.card_code(self.a)} → {deck.card_code(self.b)}"


def combinar(a: int, b: int, idioma: str = PADRAO) -> Resultado:
    """Aplica a regra matemática às duas cartas (índices 0-51, a != b)."""
    if a == b:
        raise ValueError("as duas cartas não podem ser iguais (retirada sem reposição)")
    wordlist = carregar_wordlist(idioma)
    b_ajustado = b if b < a else b - 1
    n = 51 * a + b_ajustado
    valido = n <= VALID_MAX
    palavra = wordlist[n] if valido else None
    return Resultado(a=a, b=b, b_ajustado=b_ajustado, n=n, valido=valido, palavra=palavra, idioma=idioma)


def consultar(carta1: str, carta2: str, idioma: str = PADRAO) -> Resultado:
    """Mesma coisa que `combinar`, mas recebendo notações de carta em texto."""
    a = deck.parse_card(carta1)
    b = deck.parse_card(carta2)
    return combinar(a, b, idioma=idioma)


def gerar_tabela_completa(idioma: str = PADRAO):
    """Gera (mapa, descartes) reproduzindo as abas 'Mapa BIP39' e 'Descartes' da planilha."""
    mapa = []
    descartes = []
    for a in range(52):
        for b in range(52):
            if b == a:
                continue
            r = combinar(a, b, idioma=idioma)
            if r.valido:
                mapa.append(r)
            else:
                descartes.append(r)
    mapa.sort(key=lambda r: r.n)
    descartes.sort(key=lambda r: r.n)
    return mapa, descartes


def idiomas_disponiveis() -> list[str]:
    return sorted(IDIOMAS)
