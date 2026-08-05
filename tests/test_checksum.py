"""Testes do cálculo de checksum (última palavra da frase BIP39).

Cruza o resultado com a biblioteca de referência `mnemonic` (PyPI) quando
disponível — se não estiver instalada, os testes que dependem dela são
pulados automaticamente.
"""

import pathlib
import secrets
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "src"))

from bip39_baralho import checksum, deck, mapping  # noqa: E402

try:
    from mnemonic import Mnemonic
    _TEM_MNEMONIC_LIB = True
except ImportError:
    _TEM_MNEMONIC_LIB = False


def _sortear_palavras_livres(n: int, idioma: str = "english") -> list[str]:
    rng = secrets.SystemRandom()
    palavras = []
    while len(palavras) < n:
        baralho = list(deck.full_deck())
        rng.shuffle(baralho)
        r = mapping.combinar(baralho[0], baralho[1], idioma=idioma)
        if r.valido:
            palavras.append(r.palavra)
    return palavras


def _sortear_bits_extra(idioma: str = "english") -> str:
    rng = secrets.SystemRandom()
    while True:
        baralho = list(deck.full_deck())
        rng.shuffle(baralho)
        r = mapping.combinar(baralho[0], baralho[1], idioma=idioma)
        if r.valido:
            return format(r.n, "011b")


def test_config_para_valores_conhecidos():
    assert checksum.config_para(12) == (128, 4, 7)
    assert checksum.config_para(18) == (192, 6, 5)
    assert checksum.config_para(24) == (256, 8, 3)


def test_quantidade_nao_suportada_gera_erro():
    try:
        checksum.config_para(15)
        assert False, "deveria ter levantado ValueError"
    except ValueError:
        pass


def test_mnemonic_gerada_valida_a_si_mesma():
    for n in (12, 18, 24):
        palavras = _sortear_palavras_livres(n - 1)
        bits_extra = _sortear_bits_extra()
        resultado = checksum.calcular_ultima_palavra(palavras, bits_extra)
        assert len(resultado.mnemonic) == n
        assert checksum.validar_mnemonic(resultado.mnemonic)


def test_mnemonic_adulterada_falha_validacao():
    palavras = _sortear_palavras_livres(11)
    bits_extra = _sortear_bits_extra()
    resultado = checksum.calcular_ultima_palavra(palavras, bits_extra)
    adulterada = list(resultado.mnemonic)
    adulterada[0] = "abandon" if adulterada[0] != "abandon" else "ability"
    assert checksum.validar_mnemonic(resultado.mnemonic) is True
    assert checksum.validar_mnemonic(adulterada) is False


def test_cruzamento_com_biblioteca_mnemonic_referencia():
    if not _TEM_MNEMONIC_LIB:
        return  # biblioteca 'mnemonic' não instalada; pula o teste
    mnemo = Mnemonic("english")
    for n in (12, 18, 24):
        for _ in range(10):
            palavras = _sortear_palavras_livres(n - 1)
            bits_extra = _sortear_bits_extra()
            resultado = checksum.calcular_ultima_palavra(palavras, bits_extra)
            frase = " ".join(resultado.mnemonic)
            assert mnemo.check(frase), frase
