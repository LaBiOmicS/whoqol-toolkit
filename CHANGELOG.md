# Changelog

Todas as mudanças relevantes deste projeto são documentadas aqui.
O formato segue o [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/) e o projeto adota o
[Versionamento Semântico](https://semver.org/lang/pt-BR/).

## [0.1.0] - 2026-11-10

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
