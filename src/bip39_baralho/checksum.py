"""Cálculo do checksum BIP39 (a última palavra da frase).

Uma frase BIP39 de N palavras carrega ENT bits de entropia + CS bits de
checksum, onde CS = ENT/32 e ENT + CS = 11*N. Isso dá:

    N   ENT   CS   bits "livres" na última palavra (R = 11 - CS)
    12  128   4    7
    18  192   6    5
    24  256   8    3

Ou seja: as primeiras N-1 palavras são 100% livres (11 bits cada, saem
direto do sorteio com baralho). Já a última palavra tem só R bits livres —
os CS bits finais são sempre o checksum calculado sobre toda a entropia, não
podem ser escolhidos.

Fluxo prático com baralho:
  1. Sorteie normalmente as N-1 primeiras palavras (uma consulta por palavra).
  2. Sorteie mais duas cartas (mais uma "consulta") só para gerar os R bits
     livres da última palavra — usa-se apenas os R bits mais significativos
     do resultado dessa consulta extra, o resto é descartado.
  3. Rode `finalizar` com as N-1 palavras + essa consulta extra: a ferramenta
     calcula o SHA-256 da entropia, extrai os CS bits de checksum e diz qual
     é a palavra final (índice = R bits livres + CS bits de checksum).

Isso é exatamente o que este módulo faz.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass

from .idiomas import PADRAO, carregar_wordlist

# N (nº de palavras) -> (ENT bits, CS bits, R bits livres na última palavra)
CONFIG_PALAVRAS = {
    12: (128, 4, 7),
    18: (192, 6, 5),
    24: (256, 8, 3),
}


@dataclass(frozen=True)
class ResultadoFinal:
    n_palavras: int
    ent_bits: int
    cs_bits: int
    r_bits_livres: int
    entropia_bin: str
    checksum_bin: str
    indice_ultima_palavra: int
    ultima_palavra: str
    mnemonic: list[str]


def _indices_para_bits(indices: list[int], largura: int = 11) -> str:
    return "".join(format(i, f"0{largura}b") for i in indices)


def config_para(n_palavras: int) -> tuple[int, int, int]:
    if n_palavras not in CONFIG_PALAVRAS:
        opcoes = ", ".join(str(n) for n in sorted(CONFIG_PALAVRAS))
        raise ValueError(f"quantidade de palavras não suportada: {n_palavras}. Use: {opcoes}")
    return CONFIG_PALAVRAS[n_palavras]


def calcular_ultima_palavra(
    palavras_iniciais: list[str],
    bits_extra: str,
    idioma: str = PADRAO,
) -> ResultadoFinal:
    """Calcula a última palavra (com checksum) de uma frase BIP39.

    `palavras_iniciais`: as N-1 primeiras palavras já sorteadas com baralho.
    `bits_extra`: string de bits ('0'/'1') de uma consulta extra de baralho
    (11 bits) — só os R mais significativos são usados.
    """
    n_palavras = len(palavras_iniciais) + 1
    ent_bits, cs_bits, r_bits = config_para(n_palavras)

    wordlist = carregar_wordlist(idioma)
    indice_por_palavra = {p: i for i, p in enumerate(wordlist)}

    indices = []
    for p in palavras_iniciais:
        if p not in indice_por_palavra:
            raise ValueError(f"palavra fora da wordlist '{idioma}': {p!r}")
        indices.append(indice_por_palavra[p])

    if len(bits_extra) < r_bits:
        raise ValueError(
            f"bits_extra tem {len(bits_extra)} bits, mas são necessários pelo menos "
            f"{r_bits} para completar a última palavra (frase de {n_palavras} palavras)"
        )
    bits_livres = bits_extra[:r_bits]

    entropia_bin = _indices_para_bits(indices) + bits_livres
    if len(entropia_bin) != ent_bits:
        raise ValueError(
            f"entropia com {len(entropia_bin)} bits, esperado {ent_bits} "
            f"para uma frase de {n_palavras} palavras"
        )

    entropia_bytes = int(entropia_bin, 2).to_bytes(ent_bits // 8, "big")
    digest = hashlib.sha256(entropia_bytes).digest()
    checksum_bin = "".join(format(b, "08b") for b in digest)[:cs_bits]

    ultima_bin = bits_livres + checksum_bin
    indice_ultima = int(ultima_bin, 2)
    ultima_palavra = wordlist[indice_ultima]

    return ResultadoFinal(
        n_palavras=n_palavras,
        ent_bits=ent_bits,
        cs_bits=cs_bits,
        r_bits_livres=r_bits,
        entropia_bin=entropia_bin,
        checksum_bin=checksum_bin,
        indice_ultima_palavra=indice_ultima,
        ultima_palavra=ultima_palavra,
        mnemonic=[*palavras_iniciais, ultima_palavra],
    )


def validar_mnemonic(palavras: list[str], idioma: str = PADRAO) -> bool:
    """Recalcula o checksum de uma frase completa e confirma se bate."""
    n_palavras = len(palavras)
    ent_bits, cs_bits, _ = config_para(n_palavras)

    wordlist = carregar_wordlist(idioma)
    indice_por_palavra = {p: i for i, p in enumerate(wordlist)}
    for p in palavras:
        if p not in indice_por_palavra:
            raise ValueError(f"palavra fora da wordlist '{idioma}': {p!r}")

    indices = [indice_por_palavra[p] for p in palavras]
    bits_totais = _indices_para_bits(indices)
    entropia_bin = bits_totais[:ent_bits]
    checksum_informado = bits_totais[ent_bits:]

    entropia_bytes = int(entropia_bin, 2).to_bytes(ent_bits // 8, "big")
    digest = hashlib.sha256(entropia_bytes).digest()
    checksum_calculado = "".join(format(b, "08b") for b in digest)[:cs_bits]

    return checksum_calculado == checksum_informado
