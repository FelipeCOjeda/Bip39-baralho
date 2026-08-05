# BIP39 com Baralho

Gere suas palavras BIP39 (seed phrase) usando um baralho comum de 52 cartas — sem depender de nenhum computador para a aleatoriedade.

## Por que usar um baralho?

Uma seed BIP39 só é segura se a fonte de aleatoriedade for confiável. Gerar a seed em um computador conectado à internet reintroduz o risco que o método manual existe para eliminar. Com um baralho físico, **você** controla a entropia.

## O que tem na planilha

A planilha `tabela_baralho_bip39.xlsx` contém tudo o que você precisa:

- **Consulta multilíngue** — selecione o idioma e as duas cartas sorteadas nos dropdowns; a palavra BIP39 aparece automaticamente.
- **Idiomas** — lista dos 10 idiomas oficiais do BIP-0039 (inglês, português, espanhol, francês, italiano, tcheco, japonês, coreano, chinês simplificado e chinês tradicional).
- **Quantidade de Palavras** — selecione 12, 18 ou 24 palavras para ver quantos bits de entropia, checksum e bits livres na última palavra.
- **Checksum** — explicação de como calcular a última palavra (o Excel não tem SHA-256 nativo, então essa etapa precisa ser feita com uma ferramenta offline).
- **WL_\<idioma\>** (abas ocultas) — wordlist completa de cada idioma, usada pelas fórmulas.

## Como sortear sua seed phrase

### Índice das cartas (0–51)

| Naipe | Cartas | Índices |
|---|---|---|
| Paus ♣ | A, 2, 3 … K | 0–12 |
| Ouros ♦ | A, 2, 3 … K | 13–25 |
| Copas ♥ | A, 2, 3 … K | 26–38 |
| Espadas ♠ | A, 2, 3 … K | 39–51 |

### Passo a passo

1. Embaralhe bem o baralho completo (52 cartas).
2. Retire **duas cartas** em sequência, sem reposição.
3. Abra a aba **Consulta multilíngue** da planilha, escolha o idioma e selecione as duas cartas nos dropdowns.
4. Se o resultado for **DESCARTAR**, devolva as cartas ao baralho, embaralhe novamente e repita.
5. Se o resultado for uma palavra, anote-a. Essa é uma das suas palavras BIP39.
6. Devolva as cartas, embaralhe e repita os passos 2–5 até ter **N−1 palavras** (11 para carteira de 12, 17 para 18, ou 23 para 24).

### A regra matemática (para quem quiser entender)

- `a` = índice da 1ª carta (0–51)
- `b` = índice da 2ª carta (0–51, b ≠ a)
- `b'` = b se b < a, senão b − 1
- `N = 51×a + b'`
- Se N está entre 0 e 2047 → palavra válida (wordlist[N])
- Se N está entre 2048 e 2651 → descarte

### A última palavra (checksum)

A última palavra da seed phrase não é 100% livre — ela carrega bits de checksum (SHA-256 da entropia). Por isso, **não dá para sortear todas as palavras apenas com consultas na planilha**.

| Palavras | Entropia | Checksum | Bits livres na última palavra |
|---|---|---|---|
| 12 | 128 bits | 4 bits | 7 |
| 18 | 192 bits | 6 bits | 5 |
| 24 | 256 bits | 8 bits | 3 |

Para calcular a última palavra, use o arquivo `bip39_baralho_offline.html` incluído neste repositório. Ele funciona 100% offline em qualquer navegador — basta salvar o arquivo e abrir sem internet. Ele usa a Web Crypto API (SHA-256 nativo do navegador) para calcular o checksum automaticamente.

Funcionalidades do HTML offline: consulta de cartas (duas cartas → palavra), finalização da seed phrase (insira as N-1 palavras + consulta extra → última palavra calculada), validação de frase completa (verifica checksum), autocomplete de palavras e suporte a todos os 10 idiomas.

## Aviso de segurança

Esta planilha ajuda a converter cartas físicas em palavras BIP39. Para proteger fundos reais, sorteie as cartas em um ambiente privado e nunca digite a frase completa em um computador conectado à internet.

## Licença

MIT
