# bip39-baralho

Sorteio de palavras BIP39 usando um baralho comum de 52 cartas — sem
computador no processo de geração da entropia. Implementa em código a regra
matemática da planilha `tabela_baralho_bip39.xlsx` (incluída em `docs/`) e
foi validado linha a linha contra ela (2048 combinações válidas + 604
descartes, 100% de correspondência).

Suporta as 10 wordlists oficiais do BIP-0039 (inglês, português, espanhol,
francês, italiano, tcheco, japonês, coreano, chinês simplificado e chinês
tradicional), carteiras de 12, 18 ou 24 palavras, e calcula o checksum da
última palavra (com verificação cruzada contra a biblioteca de referência
`mnemonic`).

## Por que baralho, e por que não gerar a seed no computador

Uma seed BIP39 só é tão segura quanto a fonte de aleatoriedade usada para
criá-la. Gerar a seed com o gerador aleatório de um computador conectado à
internet reintroduz o risco que o método manual existe para eliminar. Por
isso esta ferramenta é pensada para uso em dois momentos separados:

1. Sorteio físico das cartas — feito por você, longe de qualquer tela.
2. Consulta da tabela / cálculo do checksum — usados só para traduzir "quais
   cartas eu tirei" em "qual é a frase final", idealmente em um dispositivo
   offline.

O comando `demo` existe apenas para testes e validação do algoritmo; ele usa
`secrets.SystemRandom()` e não deve ser usado para gerar uma seed real.

## Como funciona

1. Embaralhe bem o baralho completo (52 cartas).
2. Retire duas cartas em sequência, sem reposição.
3. Aplique a regra:
   - `a` = índice da 1ª carta (0-51)
   - `b` = índice da 2ª carta (0-51, `b ≠ a`)
   - `b'` = `b` se `b < a`, senão `b - 1`
   - `N = 51*a + b'` (0-2651)
   - Se `N` estiver entre 0 e 2047: combinação válida, palavra = `wordlist[N]`.
   - Se `N` estiver entre 2048 e 2651: descarte. Devolva as cartas, embaralhe
     de novo e repita.
4. Repita para cada palavra da frase — exceto a última.

Índice das cartas (0-51): Paus (A-K) = 0-12, Ouros (A-K) = 13-25, Copas (A-K)
= 26-38, Espadas (A-K) = 39-51.

## Tamanho da carteira e checksum

Uma frase BIP39 de N palavras carrega `ENT` bits de entropia + `CS` bits de
checksum, onde `CS = ENT/32` e `ENT + CS = 11*N` (cada palavra = 11 bits).
Isso dá:

| Palavras | Entropia (ENT) | Checksum (CS) | Bits livres na última palavra |
|---|---|---|---|
| 12 | 128 bits | 4 bits | 7 |
| 18 | 192 bits | 6 bits | 5 |
| 24 | 256 bits | 8 bits | 3 |

Ou seja: as primeiras N-1 palavras são **100% livres** — cada uma sai de uma
consulta de baralho normal. A última palavra é diferente: só os bits "livres"
da tabela acima vêm de mais um sorteio de cartas; os bits de checksum
restantes são sempre o SHA-256 da entropia inteira, então não podem ser
escolhidos. Esta ferramenta calcula essa última palavra automaticamente (veja
o comando `finalizar` abaixo) — não dá para sortear a frase inteira só com
consultas soltas.

## Instalação

```bash
git clone <url-do-repositorio>
cd bip39-baralho
python3 -m bip39_baralho idiomas
```

Não há dependências externas para uso normal (só biblioteca padrão do
Python 3.10+). `openpyxl`, `pytest` e `mnemonic` são usados apenas para
rodar os testes.

## Uso

Converter duas cartas em palavra:

```bash
python3 -m bip39_baralho consulta A♣ 2♣
python3 -m bip39_baralho consulta AC 2C --idioma portuguese
```

Ver o passo a passo completo para sortear uma frase inteira, incluindo a
etapa de checksum (carteira de 12, 18 ou 24 palavras):

```bash
python3 -m bip39_baralho manual --palavras 12 --idioma spanish
```

Depois de sortear as N-1 primeiras palavras com `consulta` e mais um par de
cartas extra, calcular a última palavra (com checksum):

```bash
python3 -m bip39_baralho finalizar abandon ability able ... \
    --carta-extra1 10♦ --carta-extra2 A♣ --idioma english
```

Conferir se uma frase completa (N palavras) tem checksum válido:

```bash
python3 -m bip39_baralho validar abandon ability able ... zoo
```

Exportar a tabela completa (2048 combinações válidas + 604 descartes) em CSV,
em qualquer um dos 10 idiomas:

```bash
python3 -m bip39_baralho tabela --idioma french --saida-mapa mapa_fr.csv --saida-descartes descartes_fr.csv
```

Listar os idiomas suportados:

```bash
python3 -m bip39_baralho idiomas
```

Modo de demonstração/teste — gera a frase inteira (com checksum) usando o
gerador aleatório do computador. **NÃO usar para gerar seed real** (ver aviso
acima):

```bash
python3 -m bip39_baralho demo --palavras 24 --idioma english
```

## Notação de cartas aceita

O comando `consulta` aceita várias notações equivalentes: `A♣`, `AC`,
`10-Copas`, `Q Espadas`, `KS`. Naipes podem ser dados por símbolo (♣ ♦ ♥ ♠),
letra (C D H S) ou nome em português.

## Planilha

`docs/tabela_baralho_bip39.xlsx` é a planilha original enviada (inglês
apenas) — usada como referência de validação pelos testes automatizados.

`docs/tabela_baralho_bip39_multilingue.xlsx` é uma versão estendida da mesma
planilha, com tudo que o código também faz:

- aba **Idiomas** — lista dos 10 idiomas suportados;
- abas **WL_<idioma>** — wordlist completa de cada idioma (índice -> palavra);
- aba **Consulta multilíngue** — igual à aba "Consulta" original, mas com
  dropdown de idioma;
- aba **Quantidade de Palavras** — dropdown 12/18/24 com a tabela de
  ENT/CS/bits livres;
- aba **Checksum** — explicação completa do cálculo (a planilha não computa
  SHA-256 — Excel não tem essa função nativa sem VBA/macro — por isso essa
  etapa fica com a ferramenta de linha de comando).

## Testes

```bash
pip install -e ".[dev]"
pytest
```

Os testes verificam: as 10 wordlists têm 2048 palavras únicas cada, a regra
matemática bate com os exemplos conhecidos, o cálculo de checksum bate com a
biblioteca de referência `mnemonic` (quando instalada), e (se a planilha
original estiver em `docs/tabela_baralho_bip39.xlsx`) a tabela gerada bate
célula a célula com o arquivo original.

## Estrutura

```
data/                     wordlists oficiais do BIP-0039 (10 idiomas)
docs/                     planilhas de referência (original + multilíngue)
src/bip39_baralho/
  deck.py                 representação do baralho e parsing de notação de carta
  idiomas.py              carregamento das wordlists por idioma
  mapping.py              regra matemática carta -> palavra
  checksum.py             cálculo da última palavra (checksum BIP39)
  cli.py                  interface de linha de comando
tests/                    testes automatizados
```

## Aviso de segurança

Esta ferramenta ajuda a converter cartas físicas em palavras BIP39 e a
calcular o checksum — ela não substitui um bom processo de custódia. Sortear
as cartas em um ambiente privado, rodar a etapa de `finalizar`/`validar` num
dispositivo offline, e nunca digitar a frase completa em um computador
conectado à internet.

## Licença

MIT — veja `LICENSE`.
