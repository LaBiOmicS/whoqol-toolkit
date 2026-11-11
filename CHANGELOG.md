# Changelog

Todas as mudanças relevantes deste projeto são documentadas aqui.
O formato segue o [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/) e o projeto adota o
[Versionamento Semântico](https://semver.org/lang/pt-BR/).

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
