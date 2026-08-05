"""CLI: `python -m bip39_baralho <comando> ...`"""

from __future__ import annotations

import argparse
import csv
import secrets
import sys

from . import checksum, deck, mapping
from .idiomas import PADRAO

PALAVRAS_SUPORTADAS = [12, 18, 24]

AVISO_DEMO = """\
################################################################################
AVISO: este é um modo de DEMONSTRAÇÃO/TESTE. Ele usa o gerador aleatório do
computador (secrets.SystemRandom), não um baralho físico. Para gerar uma seed
BIP39 que vai proteger fundos reais, sorteie as cartas fisicamente, com um
baralho embaralhado à mão, em um dispositivo OFFLINE — nunca use este modo
"demo" para esse fim.
################################################################################
"""


def cmd_idiomas(args: argparse.Namespace) -> int:
    print("Idiomas suportados (wordlists oficiais do BIP-0039, 2048 palavras cada):")
    for nome in mapping.idiomas_disponiveis():
        print(f"  {nome}")
    return 0


def cmd_consulta(args: argparse.Namespace) -> int:
    r = mapping.consultar(args.carta1, args.carta2, idioma=args.idioma)
    print(f"Idioma:               {r.idioma}")
    print(f"Padrão:               {r.padrao}")
    print(f"Índice carta 1 (a):   {r.a}")
    print(f"Índice carta 2 (b):   {r.b}")
    print(f"Posição ajustada b':  {r.b_ajustado}")
    print(f"Número N:             {r.n}")
    if r.valido:
        print(f"Status:               VÁLIDA")
        print(f"Palavra BIP39:        {r.palavra}")
        print(f"11 bits:              {format(r.n, '011b')}")
    else:
        print(f"Status:               DESCARTAR (devolva as cartas, embaralhe e repita)")
    return 0


def cmd_tabela(args: argparse.Namespace) -> int:
    mapa, descartes = mapping.gerar_tabela_completa(idioma=args.idioma)

    with open(args.saida_mapa, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(
            ["indice_bip39", "palavra", "11_bits", "indice_carta1", "carta1", "nome_carta1",
             "b_ajustado", "indice_carta2", "carta2", "nome_carta2", "padrao"]
        )
        for r in mapa:
            w.writerow(
                [r.n, r.palavra, format(r.n, "011b"), r.a, deck.card_code(r.a), deck.card_name(r.a),
                 r.b_ajustado, r.b, deck.card_code(r.b), deck.card_name(r.b), r.padrao]
            )

    with open(args.saida_descartes, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(
            ["n", "indice_carta1", "carta1", "nome_carta1", "b_ajustado",
             "indice_carta2", "carta2", "nome_carta2", "padrao", "acao"]
        )
        for r in descartes:
            w.writerow(
                [r.n, r.a, deck.card_code(r.a), deck.card_name(r.a), r.b_ajustado,
                 r.b, deck.card_code(r.b), deck.card_name(r.b), r.padrao, "DESCARTAR"]
            )

    print(f"idioma: {args.idioma}")
    print(f"{len(mapa)} combinações válidas  -> {args.saida_mapa}")
    print(f"{len(descartes)} combinações descartadas -> {args.saida_descartes}")
    return 0


def cmd_manual(args: argparse.Namespace) -> int:
    ent_bits, cs_bits, r_bits = checksum.config_para(args.palavras)
    n_livres = args.palavras - 1
    print(f"Sorteio manual de uma frase BIP39 de {args.palavras} palavras ({args.idioma})\n")
    print(f"Entropia: {ent_bits} bits | checksum: {cs_bits} bits\n")
    print(f"Palavras 1 a {n_livres} (100% livres, uma consulta cada):")
    print("  1. Embaralhe bem o baralho completo (52 cartas).")
    print("  2. Retire duas cartas em sequência, sem reposição.")
    print(f"  3. Rode: python -m bip39_baralho consulta <carta1> <carta2> --idioma {args.idioma}")
    print("  4. Se vier 'DESCARTAR', devolva as cartas ao baralho, embaralhe de novo e repita.")
    print(f"  5. Repita os passos 1-4 até ter as {n_livres} primeiras palavras.\n")
    print(f"Palavra {args.palavras} (a última, carrega o checksum):")
    print("  6. Sorteie mais UMA consulta extra (mais duas cartas, mesmo processo acima).")
    print(f"     Só os {r_bits} bits mais significativos dela serão usados; o resto é descartado.")
    print("  7. Rode:")
    print(f"     python -m bip39_baralho finalizar {' '.join(f'PALAVRA{i}' for i in range(1, n_livres + 1))} \\")
    print("         --carta-extra1 <carta1> --carta-extra2 <carta2> --idioma " + args.idioma)
    print("     A ferramenta calcula o SHA-256 da entropia e informa a última palavra.")
    return 0


def cmd_finalizar(args: argparse.Namespace) -> int:
    r_extra = mapping.consultar(args.carta_extra1, args.carta_extra2, idioma=args.idioma)
    if not r_extra.valido:
        print(f"Consulta extra {r_extra.padrao} caiu em DESCARTE (N={r_extra.n}).")
        print("Devolva as cartas, embaralhe de novo, tire outro par e rode o comando de novo.")
        return 1
    bits_extra = format(r_extra.n, "011b")
    resultado = checksum.calcular_ultima_palavra(args.palavras, bits_extra, idioma=args.idioma)
    print(f"Frase de {resultado.n_palavras} palavras ({args.idioma})")
    print(f"Entropia:             {resultado.ent_bits} bits")
    print(f"Checksum:             {resultado.cs_bits} bits ({resultado.checksum_bin})")
    print(f"Bits livres usados:   {resultado.r_bits_livres} (da consulta extra {r_extra.padrao})")
    print(f"Última palavra:       {resultado.ultima_palavra}")
    print()
    print("Frase completa:")
    print(" ".join(resultado.mnemonic))
    return 0


def cmd_validar(args: argparse.Namespace) -> int:
    ok = checksum.validar_mnemonic(args.palavras, idioma=args.idioma)
    print("VÁLIDA (checksum confere)" if ok else "INVÁLIDA (checksum não confere)")
    return 0 if ok else 1


def cmd_demo(args: argparse.Namespace) -> int:
    print(AVISO_DEMO)
    rng = secrets.SystemRandom()
    n_livres = args.palavras - 1
    palavras = []
    for i in range(1, n_livres + 1):
        while True:
            baralho = list(deck.full_deck())
            rng.shuffle(baralho)
            a, b = baralho[0], baralho[1]
            r = mapping.combinar(a, b, idioma=args.idioma)
            print(f"  palavra {i}: {r.padrao}  N={r.n}  -> "
                  f"{'DESCARTAR, repetindo' if not r.valido else r.palavra}")
            if r.valido:
                palavras.append(r.palavra)
                break

    while True:
        baralho = list(deck.full_deck())
        rng.shuffle(baralho)
        a, b = baralho[0], baralho[1]
        r_extra = mapping.combinar(a, b, idioma=args.idioma)
        print(f"  consulta extra p/ checksum: {r_extra.padrao}  N={r_extra.n}  -> "
              f"{'DESCARTAR, repetindo' if not r_extra.valido else 'ok'}")
        if r_extra.valido:
            break
    bits_extra = format(r_extra.n, "011b")
    resultado = checksum.calcular_ultima_palavra(palavras, bits_extra, idioma=args.idioma)
    print(f"  palavra {args.palavras} (com checksum): {resultado.ultima_palavra}")

    print("\nResultado (demo, NÃO use para custódia real):")
    print(" ".join(resultado.mnemonic))
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="bip39-baralho",
        description="Sorteio de palavras BIP39 usando um baralho de 52 cartas.",
    )
    sub = p.add_subparsers(dest="comando", required=True)

    p_idiomas = sub.add_parser("idiomas", help="lista os idiomas (wordlists) suportados")
    p_idiomas.set_defaults(func=cmd_idiomas)

    p_consulta = sub.add_parser("consulta", help="converte duas cartas em uma palavra BIP39")
    p_consulta.add_argument("carta1", help="ex.: A♣, AC, 10-Copas, KS")
    p_consulta.add_argument("carta2", help="ex.: 2♣, 2C, Q-Espadas, JH")
    p_consulta.add_argument("--idioma", default=PADRAO, choices=mapping.idiomas_disponiveis())
    p_consulta.set_defaults(func=cmd_consulta)

    p_tabela = sub.add_parser("tabela", help="exporta a tabela completa (2048 válidas + 604 descartes) em CSV")
    p_tabela.add_argument("--idioma", default=PADRAO, choices=mapping.idiomas_disponiveis())
    p_tabela.add_argument("--saida-mapa", default="mapa_bip39.csv")
    p_tabela.add_argument("--saida-descartes", default="descartes.csv")
    p_tabela.set_defaults(func=cmd_tabela)

    p_manual = sub.add_parser(
        "manual", help="imprime o passo a passo para sortear uma frase completa (com checksum) com baralho físico"
    )
    p_manual.add_argument("--palavras", type=int, default=12, choices=PALAVRAS_SUPORTADAS,
                           help="tamanho da carteira: 12, 18 ou 24 palavras")
    p_manual.add_argument("--idioma", default=PADRAO, choices=mapping.idiomas_disponiveis())
    p_manual.set_defaults(func=cmd_manual)

    p_finalizar = sub.add_parser(
        "finalizar", help="calcula a última palavra (checksum) a partir das palavras já sorteadas"
    )
    p_finalizar.add_argument("palavras", nargs="+", help="as N-1 primeiras palavras já sorteadas, em ordem")
    p_finalizar.add_argument("--carta-extra1", required=True, help="1ª carta da consulta extra p/ os bits livres")
    p_finalizar.add_argument("--carta-extra2", required=True, help="2ª carta da consulta extra p/ os bits livres")
    p_finalizar.add_argument("--idioma", default=PADRAO, choices=mapping.idiomas_disponiveis())
    p_finalizar.set_defaults(func=cmd_finalizar)

    p_validar = sub.add_parser("validar", help="confere se o checksum de uma frase completa está correto")
    p_validar.add_argument("palavras", nargs="+", help="a frase completa (12, 18 ou 24 palavras), em ordem")
    p_validar.add_argument("--idioma", default=PADRAO, choices=mapping.idiomas_disponiveis())
    p_validar.set_defaults(func=cmd_validar)

    p_demo = sub.add_parser(
        "demo", help="[SOMENTE TESTE] simula a frase inteira (com checksum) digitalmente, não usar para seeds reais"
    )
    p_demo.add_argument("--palavras", type=int, default=12, choices=PALAVRAS_SUPORTADAS)
    p_demo.add_argument("--idioma", default=PADRAO, choices=mapping.idiomas_disponiveis())
    p_demo.set_defaults(func=cmd_demo)

    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
