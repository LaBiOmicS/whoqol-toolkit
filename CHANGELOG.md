# Changelog

Todas as mudanças relevantes deste projeto são documentadas aqui.
O formato segue o [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/) e o projeto adota o
[Versionamento Semântico](https://semver.org/lang/pt-BR/).

## [Não lançado]

### Adicionado
- Análise de sensibilidade das regras de pontuação: onde o manual ou a sintaxe oficial são omissos ou divergem, os
  dados são repontuados com cada regra alternativa documentada (sintaxe da UFRGS, texto do manual, ausência de regra)
  e o relatório mostra a mudança nas médias e no número de participantes pontuados (seção do `report.md`, aba
  `scoring_sensitivity` do `results.xlsx`, chave `scoring_sensitivity` do `results.json`, frases nos textos de
  métodos e resultados). Alerta quando uma média muda ≥ 0,2 DP ou o n muda ≥ 5%.
- Notas de métodos que declaravam só no guia de pontuação as divergências entre fontes: EUROHIS-QOL 8 (soma, e não a
  média da sintaxe da UFRGS; oito itens exigidos), WHOQOL-HIV e WHOQOL-100 + SRPB (F2.1 não invertido) e WHOQOL-DIS
  (manual da OMS, não a sintaxe brasileira).
- Página do projeto: seção "Instrumentos" (PT/EN/ES) com a definição de qualidade de vida da OMS, a importância dos
  instrumentos, tabela comparativa (quando usar cada um), explicação do cálculo do escore com exemplo trabalhado e
  ficha de cada questionário (estrutura, regra de pontuação, pontos de atenção e versões validadas).

## [0.3.0] — 2026-11-11

### Adicionado
- Catorze chaves de instrumento além do WHOQOL-BREF, entre elas: WHOQOL-OLD, EUROHIS-QOL 8 (também a partir de uma planilha do
  WHOQOL-BREF), WHOQOL-HIV-BREF, WHOQOL-SRPB BREF, módulo WHOQOL-SRPB, WHOQOL-DIS para incapacidades físicas e
  intelectuais (escalas de 3 pontos), WHOQOL-100, WHOQOL-HIV (120 itens) e WHOQOL-100 + SRPB. Regras transcritas dos
  manuais da OMS e das sintaxes oficiais (distribuídas pelo grupo WHOQOL da UFRGS); textos dos itens em português
  dos formulários brasileiros.
- Modelo de instrumento generalizado: escores como média × multiplicador (soma no WHOQOL-OLD, DIS e EUROHIS),
  domínios compostos pela média de facetas com facetas invertidas (24 − faceta), escores totais oficiais, escalas de
  resposta por item (1–3 na versão ID do DIS), códigos de itens nos cabeçalhos (`F1.1`, `F11`, `old_01`, `HBREF_1`,
  `SP1.1`, `dis_01`) e numeração do formulário.
- `guide instruments` (`references/instruments.md`): qual chave usar, fontes de cada regra, convenções adotadas onde
  as fontes são omissas e divergências entre fontes (EUROHIS soma × média; F2.1 invertido por engano nas sintaxes
  do WHOQOL-HIV e do SRPB; pontuação do DIS na sintaxe brasileira × manual da OMS; regra de ausentes do WHOQOL-100
  no texto × na sintaxe). O guia `scoring` de cada instrumento traz as notas, e o rascunho de métodos declara as
  convenções.
- WHOQOL-DIS nos formulários brasileiros: itens nacionais Q40–Q43 pontuados como na sintaxe da UFRGS
  (`whoqol-dis-br`, `whoqol-dis-id-br`) e versão por representante (proxy) para incapacidade intelectual
  (`whoqol-dis-id-proxy`, escalas de 5 pontos, textos em terceira pessoa; Schmidt et al., 2010).
- `whoqol-100-bref`: os quatro domínios do WHOQOL-BREF calculados a partir de uma planilha do WHOQOL-100 ou do
  WHOQOL-HIV (códigos do apêndice 8 do manual da OMS), para comparação com estudos que usaram o WHOQOL-BREF.
- Textos em inglês das 100 questões do WHOQOL-100 (apêndice 4 do manual), reconhecidos nos cabeçalhos também no
  WHOQOL-HIV e no WHOQOL-100 + SRPB.
- AFC em Python por facetas nos instrumentos longos (escores das facetas como indicadores dos domínios) e figura de
  respostas por item desenhada por domínio acima de 40 itens.
- Testes de referência para cada instrumento, com as regras transcritas das fontes e respondentes calculados à mão.

### Alterado
- O texto de métodos descreve a pontuação de cada instrumento (somas, facetas, mínimos por escore); o do
  WHOQOL-BREF não muda.
- Psicometria dos instrumentos longos: confiabilidade, análise multitraço e HTMT por faceta; AFC de segunda ordem
  por itens no script lavaan.
- `results.json`: `descriptives_raw_4_20` passa a ser `descriptives_raw`, com a amplitude de cada escore.

## [0.2.0] — 2026-11-11

### Alterado
- O whoqol-toolkit agora é um plugin de Claude Code e Antigravity no mesmo formato do academic-peer-review e do
  congress-abstract-review: a skill roda `skills/whoqol/scripts/whoqol_cli.py` com `uv run`, que declara as
  dependências (PEP 723). O pacote foi para `skills/whoqol/scripts/whoqol/` e os guias metodológicos para
  `skills/whoqol/references/`, onde o agente os lê diretamente.
- Marketplace único `labiomics`: o `marketplace.json` dos três repositórios LaBiOmicS lista os três plugins, e
  `whoqol-toolkit@labiomics` substitui `whoqol-toolkit@labiomics-whoqol`.
- `install.sh` no formato dos outros plugins: sem o `agy` no PATH, copia o plugin para
  `~/.gemini/antigravity-cli/plugins/`.
- READMEs reorganizados como os dos outros plugins (instalação por CLI, uso interativo e sem agente, custo).
- Python 3.14 suportado (a suíte de testes passa; o limite `<3.14` foi removido).

### Adicionado
- Regras de integridade: texto de interpretação e de métodos/resultados como rascunho assistido por IA, com aviso e
  lembrete de declaração de uso de IA; idioma do relatório (`rules/AGENTS.md`).
- Defesa contra conteúdo malicioso na planilha (`security.py`): o `inspect` mostra cabeçalhos e valores limpos
  (sem caracteres ocultos ou de controle bidirecional, com tamanho limitado) e lista em `security_flags` os que
  parecem instruções a uma IA, em português, inglês e espanhol. Colunas podem ser indicadas pela posição (`#n`) em
  `--mapping`, `-g`, `-c`, `--covariate` e `--id-column`.
- Testes de referência da pontuação escritos a partir do manual da OMS, independentes da definição do instrumento:
  respondente calculado à mão nos quatro domínios, itens invertidos, mínimo de itens válidos em cada domínio, média
  dos itens respondidos, exclusão com menos de 21 itens e extremos da escala; testes da sanitização e do script de
  entrada da skill.

### Removido
- Servidor MCP (`whoqol-mcp`, `.mcp.json`, `mcp_config.json`) e a dependência `mcp`.
- Extensão do Gemini CLI (`gemini-extension.json`, `commands/whoqol.toml`) e o comando `/whoqol`; no Claude Code a
  skill é chamada por `/whoqol-toolkit:whoqol` ou pelo pedido em linguagem natural.

## [0.1.0] — 2026-11-10

### Adicionado
- Primeira versão do **whoqol-toolkit**, com o WHOQOL-BREF como primeiro instrumento.
- Registro de instrumentos (`src/whoqol/instruments/`), para incluir outros instrumentos WHOQOL sem alterar a análise.
- Pontuação pelas regras da OMS: itens invertidos (Q3, Q4, Q26), escores 4–20 e 0–100, mínimo de itens válidos por
  domínio e exclusão de questionários com menos de 21 itens válidos.
- Detecção automática das colunas pelo número ou pelo texto da pergunta em português, inglês e espanhol, e
  recodificação de respostas em texto nas três línguas.
- Detecção da versão linguística aplicada (pt-BR, es-ES, en), citada no texto de métodos.
- Qualidade dos dados, confiabilidade (α com IC de Feldt, ω, EPM, MMD95), validade (multitraço, HTMT, AFC por ML e
  script lavaan para WLSMV), comparações entre grupos com tamanho de efeito e correção de Holm, correlações,
  regressão com erros HC3, comparação com valores de referência e ponto de corte.
- Relatório, tabelas APA (DOCX), planilha de resultados (XLSX) e figuras no idioma do questionário; rascunho de
  métodos e resultados em português, inglês e espanhol.
- Dicionário de dados opcional e pré-preenchido (`whoqol_template`), com abas e papéis aceitos nas três línguas.
- Servidor MCP (`whoqol-mcp`) e linha de comando (`whoqol`); skill `whoqol`, comando `/whoqol` e regras de
  integridade e proteção de dados (`rules/AGENTS.md`).
- Logo (`assets/`) na mesma linha visual dos demais plugins LaBiOmicS e página do projeto trilíngue
  (`site/`, publicada pelo GitHub Pages).
- Manifestos para Claude Code (marketplace `labiomics-whoqol`), Antigravity e Gemini CLI; `install.sh`; CI com ruff
  e pytest em Python 3.10 e 3.12.
