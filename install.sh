#!/usr/bin/env bash
# ==============================================================================
# whoqol-toolkit: script de instalação e sincronização via uv
# LaBiOmicS / UMC - Prof. Dr. Fabiano Bezerra Menegidio
# ==============================================================================
set -e

PLUGIN_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLUGIN=whoqol-toolkit
MARKET=labiomics

echo "==> [1/4] Verificando o uv..."
if ! command -v uv &> /dev/null; then
    echo "Aviso: 'uv' não encontrado no PATH. Instalando pelo script oficial da Astral..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH"
fi
echo "✔ uv detectado: $(uv --version)"

echo "==> [2/4] Sincronizando as dependências Python..."
cd "$PLUGIN_DIR"
uv sync

copy_plugin_files() {
    local target_dir="$1"
    mkdir -p "$target_dir"
    if command -v rsync &> /dev/null; then
        rsync -a --delete --exclude='.git' --exclude='.venv' "$PLUGIN_DIR/" "$target_dir/"
    else
        rm -rf "${target_dir:?}"/*
        find "$PLUGIN_DIR" -maxdepth 1 ! -name '.git' ! -name '.venv' ! -name "$(basename "$PLUGIN_DIR")" -exec cp -r {} "$target_dir/" \;
    fi
}

# Ferramentas em que o plugin foi registrado pelo próprio CLI, e avisos para o resumo final.
INSTALLED=()
NOTES=()

echo "==> [3/4] Instalando e ativando no Antigravity CLI..."
if command -v agy &> /dev/null; then
    agy plugin install "$PLUGIN_DIR"
    agy plugin enable "$PLUGIN" || true
    echo "✔ Plugin validado no Antigravity CLI:"
    agy plugin validate "$PLUGIN_DIR" --strict
    INSTALLED+=("Antigravity CLI")
else
    echo "Aviso: 'agy' não encontrado no PATH. Copiando para o diretório padrão de plugins..."
    copy_plugin_files "$HOME/.gemini/antigravity-cli/plugins/$PLUGIN"
    NOTES+=("Antigravity: arquivos copiados para ~/.gemini/antigravity-cli/plugins, sem validação nem ativação ('agy' não está no PATH).")
fi

echo "==> [4/4] Instalando no Claude Code (marketplace local '$MARKET')..."
if command -v claude &> /dev/null; then
    claude plugin validate "$PLUGIN_DIR"
    # O marketplace 'labiomics' é compartilhado: o marketplace.json de cada repositório LaBiOmicS
    # (academic-peer-review, congress-abstract-review, whoqol-toolkit) lista os três plugins. Quando ele
    # aponta para outro caminho (outro repositório LaBiOmicS, ou um caminho antigo que faz o plugin deixar
    # de carregar com "cache-miss"), o registro é refeito neste diretório. Remover um marketplace desinstala
    # todos os plugins dele, então os outros plugins LaBiOmicS instalados são reinstalados em seguida.
    REGISTERED_PATH="$(claude plugin marketplace list --json 2>/dev/null | uv run --no-project python -c '
import json, sys
for m in json.load(sys.stdin):
    if m.get("name") == "labiomics":
        print(m.get("path") or m.get("installLocation") or "")
' 2>/dev/null || true)"
    REINSTALL=()
    if [ -n "$REGISTERED_PATH" ] && [ "$REGISTERED_PATH" != "$PLUGIN_DIR" ]; then
        # Sem a lista de plugins instalados não dá para reinstalá-los: mantém o registro atual.
        if LABIOMICS_PLUGINS="$(claude plugin list --json 2>/dev/null | uv run --no-project python -c '
import json, sys
for p in json.load(sys.stdin):
    name, _, market = p.get("id", "").partition("@")
    if market == "labiomics":
        print(p.get("scope", "user"), name)
')"; then
            while read -r scope name; do
                [ -z "$name" ] || [ "$name" = "whoqol-toolkit" ] && continue
                if [ "$scope" = "user" ]; then
                    REINSTALL+=("$name")
                else
                    NOTES+=("Claude Code: $name@labiomics (escopo $scope) foi desinstalado ao registrar o marketplace de novo; reinstale-o no projeto em que estava com 'claude plugin install $name@labiomics --scope $scope'.")
                fi
            done <<< "$LABIOMICS_PLUGINS"
            echo "Aviso: marketplace 'labiomics' registrado em $REGISTERED_PATH. Registrando de novo em $PLUGIN_DIR..."
            claude plugin marketplace remove labiomics
            REGISTERED_PATH=""
        else
            echo "Aviso: não foi possível listar os plugins instalados; o marketplace 'labiomics' continua em $REGISTERED_PATH."
            NOTES+=("Claude Code: marketplace 'labiomics' mantido em $REGISTERED_PATH; whoqol-toolkit foi instalado a partir dele, não deste diretório.")
            REGISTERED_PATH="$PLUGIN_DIR"  # só atualiza o registro existente
        fi
    fi
    if [ "$REGISTERED_PATH" = "$PLUGIN_DIR" ]; then
        claude plugin marketplace update labiomics
    else
        # Sem o caminho registrado (ex.: CLI sem --json), cai no comportamento anterior.
        claude plugin marketplace add "$PLUGIN_DIR" || claude plugin marketplace update labiomics
    fi
    claude plugin install whoqol-toolkit@labiomics
    for name in "${REINSTALL[@]}"; do
        if claude plugin install "$name@labiomics"; then
            echo "✔ $name reinstalado (marketplace 'labiomics' registrado de novo)."
        else
            NOTES+=("Claude Code: falha ao reinstalar $name@labiomics; rode 'claude plugin install $name@labiomics'.")
        fi
    done
    echo "✔ Plugin instalado no Claude Code (reinicie a sessão para carregá-lo)."
    INSTALLED+=("Claude Code")
else
    echo "Aviso: 'claude' não encontrado no PATH. Pulando a integração com o Claude Code."
    NOTES+=("Claude Code: não instalado, 'claude' não está no PATH (rode este script de novo depois de instalá-lo).")
fi

echo ""
echo "================================================================================"
if [ ${#INSTALLED[@]} -gt 0 ]; then
    JOINED="$(printf '%s, ' "${INSTALLED[@]}")"
    echo "✔ $PLUGIN registrado em: ${JOINED%, }"
else
    echo "Aviso: $PLUGIN não foi registrado em nenhum CLI."
fi
for note in "${NOTES[@]}"; do
    echo "  - $note"
done
echo "  - Ambiente virtual uv: $PLUGIN_DIR/.venv"
echo "  - Para testar: uv run skills/whoqol/scripts/whoqol_cli.py analyze examples/sample_google_forms_pt.xlsx -g Sexo"
echo "================================================================================"
