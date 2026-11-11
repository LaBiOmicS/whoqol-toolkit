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
    # Se o repositório mudou de lugar, o marketplace aponta para o caminho antigo; refaz o registro.
    REGISTERED_PATH="$(claude plugin marketplace list --json 2>/dev/null | uv run --no-project python -c '
import json, sys
for m in json.load(sys.stdin):
    if m.get("name") == "'"$MARKET"'":
        print(m.get("path") or m.get("installLocation") or "")
' 2>/dev/null || true)"
    if [ -n "$REGISTERED_PATH" ] && [ "$REGISTERED_PATH" != "$PLUGIN_DIR" ]; then
        echo "Aviso: marketplace '$MARKET' registrado em $REGISTERED_PATH. Registrando de novo em $PLUGIN_DIR..."
        claude plugin marketplace remove "$MARKET"
        REGISTERED_PATH=""
    fi
    if [ "$REGISTERED_PATH" = "$PLUGIN_DIR" ]; then
        claude plugin marketplace update "$MARKET"
    else
        claude plugin marketplace add "$PLUGIN_DIR" || claude plugin marketplace update "$MARKET"
    fi
    claude plugin install "$PLUGIN@$MARKET"
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
