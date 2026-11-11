# whoqol-toolkit

<img src="assets/logo.svg" alt="" width="120" align="right">

[![Status: beta](https://img.shields.io/badge/status-beta-orange.svg)](https://github.com/LaBiOmicS/whoqol-toolkit/issues)
[![CI](https://github.com/LaBiOmicS/whoqol-toolkit/actions/workflows/ci.yml/badge.svg)](https://github.com/LaBiOmicS/whoqol-toolkit/actions/workflows/ci.yml)
[![Release](https://img.shields.io/github/v/release/LaBiOmicS/whoqol-toolkit)](https://github.com/LaBiOmicS/whoqol-toolkit/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org)
[![Project page](https://img.shields.io/badge/docs-GitHub%20Pages-0b6e4f.svg)](https://labiomics.github.io/whoqol-toolkit/)

[English](README.md) · **Português** · [Español](README.es.md)

> [!WARNING]
> **Beta.** A ferramenta ainda pode conter erros. Confira todo resultado antes de publicá-lo e
> [relate problemas](https://github.com/LaBiOmicS/whoqol-toolkit/issues).

Plugin para **Claude Code** e **Antigravity (`agy`)** que pontua e analisa questionários de qualidade
de vida WHOQOL para publicação. Você fornece a planilha exportada do Google Forms, REDCap, LimeSurvey, SPSS ou Excel;
a ferramenta aplica as regras oficiais de pontuação da OMS, verifica a qualidade dos dados, estima confiabilidade e
validade, compara grupos e gera tabelas no estilo APA, figuras e um rascunho das seções de métodos e resultados.

Todos os números vêm de um pacote Python determinístico e testado, que a skill executa com `uv run`. O agente faz
as perguntas certas, executa os scripts e interpreta a saída; nunca calcula escores por conta própria.

Instrumentos suportados: **WHOQOL-BREF, WHOQOL-OLD, EUROHIS-QOL 8, WHOQOL-HIV-BREF, WHOQOL-SRPB BREF, WHOQOL-SRPB,
WHOQOL-DIS (incapacidades físicas e intelectuais), WHOQOL-100, WHOQOL-HIV e WHOQOL-100 + SRPB**. Cada um é pontuado
pelas regras do manual da OMS ou da sintaxe oficial; onde as fontes são omissas ou divergem, a convenção adotada está
documentada e aparece no rascunho de métodos ([instruments.md](skills/whoqol/references/instruments.md)).

---

## Sumário

- [Visão geral](#visão-geral)
- [Fluxo](#fluxo)
- [Análises](#análises)
- [Segurança e confidencialidade](#segurança-e-confidencialidade)
- [Instalação](#instalação)
- [Uso](#uso)
- [Dicionário de dados (opcional)](#dicionário-de-dados-opcional)
- [Parâmetros](#parâmetros)
- [Saídas](#saídas)
- [Limitações](#limitações)
- [Desenvolvimento](#desenvolvimento)
- [Citação](#citação)
- [Licença e autoria](#licença-e-autoria)

---

## Visão geral

| | |
|---|---|
| **Hosts** | Claude Code (plugin) · Antigravity CLI (plugin) · linha de comando |
| **Instrumentos** | WHOQOL-BREF, WHOQOL-OLD, EUROHIS-QOL 8, WHOQOL-HIV-BREF, WHOQOL-SRPB BREF, WHOQOL-SRPB, WHOQOL-DIS (físicas, intelectuais, itens nacionais, proxy), WHOQOL-100 (6 domínios ou os 4 do BREF), WHOQOL-HIV, WHOQOL-100 + SRPB ([detalhes](skills/whoqol/references/instruments.md)) |
| **Formatos de entrada** | .xlsx, .xls, .ods, .csv, .tsv, .sav |
| **Detecção dos itens** | pelo número (`Q1`, `1.`, `item_1`, `pergunta 1`, `pregunta 1`) ou pelo texto da pergunta em português, inglês ou espanhol; respostas numéricas (1–5) ou em texto |
| **Idiomas** | Português, inglês e espanhol. O relatório segue o idioma do questionário (inglês para qualquer outro); o rascunho de métodos/resultados é sempre gerado nos três |
| **Versão linguística** | detectada pelas respostas e cabeçalhos (pt-BR: Fleck et al., 2000; es-ES: Lucas, 1998; en: WHOQOL Group, 1998) e citada no texto de métodos |
| **Execução** | Python ≥ 3.10, dependências resolvidas pelo `uv`; roda localmente, sem serviços externos |

## Fluxo

```mermaid
flowchart LR
    A["Planilha"] --> B["1 · inspect<br/>colunas dos itens, versão<br/>linguística, outras variáveis"]
    M["Dicionário de dados<br/>(opcional, pré-preenchido)"] -.-> C
    B --> C["2 · combinar o plano<br/>grupos, covariáveis,<br/>valores de referência"]
    C --> D["3 · analyze<br/>pontuação OMS, qualidade,<br/>psicometria, estatística"]
    D --> E["4 · interpretação<br/>pelo agente, no idioma<br/>do usuário"]
    D --> F["report.md · tables.docx<br/>results.xlsx · figuras<br/>methods_results_pt/en/es.md"]
```

## Análises

| Área | O que é calculado |
|---|---|
| **Pontuação** | regras da OMS: Q3, Q4 e Q26 invertidos; domínio = média × 4 (4–20) e 0–100; mínimo de itens válidos por domínio (6/7, 5/6, 2/3, 6/8); exclusão de questionários com menos de 21 itens válidos; faceta global (Q1–Q2) relatada à parte |
| **Qualidade dos dados** | ausentes por item e no total, respostas não reconhecidas, exclusões, duplicatas, respostas idênticas em todos os itens, efeitos piso/teto |
| **Sensibilidade da pontuação** | onde as fontes oficiais são omissas ou divergem, os dados são repontuados com cada regra alternativa documentada (por exemplo, a sintaxe da UFRGS) e a mudança nas médias e no n é relatada |
| **Confiabilidade** | α de Cronbach com IC 95% de Feldt, ω de McDonald, r interitem médio, EPM, MMD95, ½ DP |
| **Validade** | análise multitraço (r item-domínio corrigido), HTMT, análise fatorial confirmatória (ML: χ², CFI, TLI, RMSEA com IC 90%, SRMR, AVE, CC) e script lavaan pronto para WLSMV |
| **Comparações** | t de Welch / g de Hedges, Mann-Whitney / r rank-bisserial, ANOVA de Welch / ω² + Games-Howell, Kruskal-Wallis / ε² + Dunn; correção de Holm; escolha automática por Shapiro-Wilk/TLC (relatada) |
| **Associações** | ρ de Spearman com IC 95%; regressão linear múltipla com erros HC3 e VIF |
| **Valores de referência** | comparação com médias publicadas (fornecidas pelo usuário, com a fonte); proporção acima de um ponto de corte, opcional |

## Segurança e confidencialidade

- Tudo roda localmente: o código de análise não faz chamadas de rede e a ferramenta nunca envia a planilha. O agente
  que você usa (Claude, Antigravity) vê as saídas dos scripts, que são estatísticas agregadas; evite colar linhas
  brutas no chat.
- Respostas a questionários são dados pessoais de saúde (LGPD, GDPR). Use IDs pseudonimizados, mantenha os arquivos
  fora do repositório (o `.gitignore` exclui `data/`, `*_whoqol/` e planilhas) e siga a aprovação do comitê de ética.
- Valores das células e nomes de colunas são tratados como dados, nunca como instruções ao agente. O `inspect` os
  mostra limpos (sem caracteres ocultos, com tamanho limitado) e lista em `security_flags` cabeçalhos ou células que
  parecem instruções a uma IA.
- A interpretação e o texto de métodos e resultados são rascunhos assistidos por IA: confira-os, assuma a
  responsabilidade por eles e declare o uso de IA conforme a revista exigir.
- Pontuação, estatística e relatórios vêm de código testado; o agente é instruído a nunca calcular nem inventar
  números, normas ou pontos de corte (`rules/AGENTS.md`).

## Instalação

**Requisitos:** [`uv`](https://docs.astral.sh/uv/) e Claude Code ou Antigravity CLI, instalados e autenticados. As
dependências Python são instaladas pelo `uv` na primeira vez que a skill roda.

### Claude Code

```text
/plugin marketplace add LaBiOmicS/whoqol-toolkit
/plugin install whoqol-toolkit@labiomics
```

O marketplace `labiomics` reúne todos os plugins do LaBiOmicS (academic-peer-review, congress-abstract-review,
whoqol-toolkit).

### Script de instalação (Claude Code e Antigravity)

```bash
git clone https://github.com/LaBiOmicS/whoqol-toolkit.git
cd whoqol-toolkit
./install.sh
```

O script sincroniza o ambiente Python e registra o plugin nos CLIs que estiverem instalados.

### Antigravity CLI

```bash
agy plugin validate ./whoqol-toolkit --strict
agy plugin install ./whoqol-toolkit
agy plugin enable whoqol-toolkit
```

Reinicie a sessão depois de instalar. Um passo a passo para iniciantes está na
[página do projeto](https://labiomics.github.io/whoqol-toolkit/).

## Uso

### Interativo

> Analise esta planilha do WHOQOL-BREF e compare os domínios por sexo e escolaridade: `~/dados/whoqol.xlsx`

> Avalie a confiabilidade e a validade do WHOQOL-BREF em `~/dados/pesquisa.csv` e gere tabelas para publicação.

> Analyse the WHOQOL-BREF answers in `~/data/qol_survey.xlsx`.

No Claude Code a skill também pode ser chamada diretamente: `/whoqol-toolkit:whoqol ~/dados/whoqol.xlsx`. O agente
inspeciona o arquivo, confirma com você as colunas detectadas e o plano de análise, executa a análise e interpreta os
resultados.

### Sem agente

Os mesmos scripts rodam sem agente:

```bash
WHOQOL="uv run skills/whoqol/scripts/whoqol_cli.py"
$WHOQOL inspect examples/sample_google_forms_pt.xlsx
$WHOQOL template examples/sample_google_forms_pt.xlsx --lang pt -o dicionario.xlsx
$WHOQOL analyze examples/sample_google_forms_pt.xlsx -g Sexo -g Escolaridade -c Idade
$WHOQOL analyze examples/sample_numeric.csv -g Sexo --lang pt --instrument-version pt
$WHOQOL guide scoring
```

| Comando | Função |
|---|---|
| `instruments` | lista os instrumentos e versões linguísticas suportados |
| `inspect` | detecta as colunas dos itens, a versão linguística, respostas não reconhecidas, o papel das demais colunas e conteúdo suspeito |
| `template` | cria um dicionário de dados pré-preenchido (.xlsx) em PT, EN ou ES |
| `score` | apenas pontua, uma linha por participante |
| `analyze` | análise completa e todos os arquivos de saída |
| `guide` | fluxo de trabalho, regras de pontuação, critérios psicométricos, interpretação, checklist de relato, referências |

### Custo

A análise roda localmente e não consome chamadas ao modelo. A parte do agente são poucos turnos: inspecionar, combinar
o plano e interpretar o resumo em JSON.

## Dicionário de dados (opcional)

O arquivo de metadados **nunca é obrigatório**: uma planilha com cabeçalhos claros é analisada como está. Ele ajuda
quando há variáveis codificadas (`1`/`2` em vez de rótulos), categorias ordinais (escolaridade, renda), códigos de
ausente (`99`, `-9`) ou quando você quer registrar o contexto do estudo. O comando `template` gera o arquivo já
preenchido com os papéis detectados; você revisa duas abas e o informa em `--metadata`:

- **variaveis** – coluna, papel (`item`, `id`, `grupo`, `continua`, `covariavel`, `ignorar`), item, rótulo, rótulos
  dos valores (`1=Feminino; 2=Masculino`), ordem dos níveis, códigos de ausente;
- **estudo** – população, delineamento, país, modo de aplicação.

Nomes de abas e colunas são aceitos em português, inglês ou espanhol. Uma aba `variaveis`/`variables` dentro da própria
planilha de dados é lida automaticamente.

## Parâmetros

Opções de `whoqol_cli.py analyze`:

| Opção | Padrão | Descrição |
|---|---|---|
| `-i/--instrument` | `whoqol-bref` | chave do instrumento (`instruments`) |
| `--mapping` | automático | `{"Q1": "coluna", …}` (JSON ou arquivo .json) quando a detecção falha; a coluna pode ser dada como `#n` |
| `-g/--group`, `-c/--continuous`, `--covariate` | — | variáveis para comparações, correlações e regressão (repetíveis) |
| `--method` | `auto` | `parametric`, `nonparametric` ou `auto` (Shapiro-Wilk / TLC) |
| `--reference` | — | `{"physical": {"mean": …, "sd": …, "n": …, "source": "…"}}` |
| `--cutoff` | — | proporção igual ou acima de um ponto de corte (ex.: 60, apenas idosos) |
| `--include-total` | desligado | inclui um escore total de 24 itens (não previsto no manual da OMS) |
| `--no-cfa` | desligado | pula a análise fatorial confirmatória |
| `--lang` | `auto` | idioma do relatório: `auto`, `pt`, `en`, `es` |
| `--instrument-version` | `auto` | versão linguística aplicada, citada no texto de métodos |
| `--metadata` | — | dicionário de dados; opções explícitas têm precedência |
| `-o/--output-dir` | `<arquivo>_whoqol/` | pasta de saída |

## Saídas

Gravadas em `<arquivo>_whoqol/` (ou `-o/--output-dir`):

| Arquivo | Conteúdo |
|---|---|
| `report.md` | relatório completo com alertas, tabelas, sensibilidade das regras de pontuação e figuras (no idioma do relatório) |
| `tables.docx` | tabelas no estilo APA, figuras e referências, para revisar e adaptar ao manuscrito |
| `results.xlsx` | escores por participante e todas as tabelas, uma aba cada (`scoring_sensitivity`: cada escore com cada regra alternativa) |
| `methods_results_{pt,en,es}.md` | rascunho das seções de análise estatística e resultados nos três idiomas |
| `figures/` | distribuição dos domínios, respostas por item, correlações, médias por grupo (PNG 300 dpi + PDF) |
| `cfa_wlsmv_lavaan.R` + `items_reversed.csv` | AFC com WLSMV no R (lavaan, semTools) |
| `results.json` | resumo legível por máquina (chaves em inglês) |

## Limitações

- **Não existem pontos de corte oficiais da OMS** nem diferença mínima importante estabelecida; a ferramenta relata
  referências baseadas na distribuição (½ DP, MMD95). Valores normativos devem vir de uma fonte citada.
- A AFC embutida usa máxima verossimilhança, que trata itens Likert como contínuos. Para um artigo psicométrico,
  rode o script WLSMV e teste a invariância de medida.
- A detecção da versão linguística depende de respostas em texto ou dos enunciados; com dados numéricos, informe a versão.
- Regras de dados ausentes que as fontes não definem, e a pontuação da versão por representante (proxy) do
  WHOQOL-DIS, são convenções do toolkit, listadas em [instruments.md](skills/whoqol/references/instruments.md) e
  declaradas no rascunho de métodos. Toda análise repontua os dados com as alternativas documentadas e mostra quanto
  mudam as médias e o n; leia essa seção antes de comparar com estudos pontuados pela sintaxe da UFRGS (ela inverte
  por engano o item F2.1 do WHOQOL-HIV, o que rebaixa a faceta energia e o domínio físico).
- WHOQOL-BREF-ID (incapacidades intelectuais, itens de 3 pontos): nenhuma fonte define a transformação 0–100 dos
  domínios do BREF; a transformação linear usada é uma convenção, e esses escores não são comparáveis com normas do
  BREF de cinco pontos.
- No WHOQOL-100, no WHOQOL-HIV e no WHOQOL-SRPB, a numeração das questões segue o formulário brasileiro (o formulário
  genérico da OMS não tem numeração); use os códigos dos itens (`F1.1`, `SP1.1`) ou o texto da questão nos cabeçalhos.
- Na família WHOQOL-100, a AFC em Python é feita por facetas; o modelo de segunda ordem por itens está no script lavaan.
- O uso dos instrumentos WHOQOL deve seguir os termos da OMS; o toolkit não distribui o questionário.
- Respostas a questionários são dados pessoais de saúde: mantenha-os locais e pseudonimizados (veja `rules/AGENTS.md`).

## Desenvolvimento

```bash
uv sync --group dev
uv run pytest -q
uvx ruff check skills tests examples
uv run python examples/generate_examples.py   # dados de exemplo sintéticos
claude plugin validate . && agy plugin validate . --strict
```

Para incluir um instrumento, crie `skills/whoqol/scripts/whoqol/instruments/<nome>.py` com um `Instrument` (itens, itens
invertidos, escores com mínimo de itens válidos, multiplicador ou facetas, escala de resposta, textos e códigos dos
itens, versões linguísticas, notas sobre as fontes) e registre-o em `instruments/__init__.py`. Pontuação, psicometria,
relatórios e o guia de pontuação decorrem dessa definição. Inclua um teste em `tests/test_reference_instruments.py`
com as regras transcritas do manual e um respondente calculado à mão.

## Citação

```bibtex
@software{menegidio_whoqol_toolkit_2026,
  author  = {Menegidio, Fabiano Bezerra},
  title   = {whoqol-toolkit: scoring, psychometrics and publication-grade statistics for WHOQOL questionnaires},
  year    = {2026},
  version = {0.3.0},
  url     = {https://github.com/LaBiOmicS/whoqol-toolkit}
}
```

Cite também o instrumento e a versão linguística validada utilizada (veja [references.md](skills/whoqol/references/references.md)).

## Licença e autoria

[MIT](LICENSE) © 2026 Prof. Dr. Fabiano Bezerra Menegidio — Laboratório de Bioinformática e Ciências Ômicas
(LaBiOmicS), Universidade de Mogi das Cruzes (UMC).
