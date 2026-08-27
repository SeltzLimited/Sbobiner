#!/usr/bin/env bash
# Configurazione una-tantum. Richiede connessione internet solo adesso.
set -euo pipefail
cd "$(dirname "$0")"

[[ "$(uname -m)" == "arm64" ]] || { echo "Serve un Mac Apple Silicon (arm64)."; exit 1; }
python3 -c 'import sys; sys.exit(0 if sys.version_info >= (3,9) else 1)' \
  || { echo "Serve Python 3.9 o superiore."; exit 1; }

echo "==> Creo l'ambiente virtuale (.venv)"
if command -v uv >/dev/null 2>&1; then
  uv venv .venv
else
  python3 -m venv .venv
fi
# shellcheck disable=SC1091
source .venv/bin/activate

echo "==> Installo le dipendenze"
pip install -q -U pip
pip install -q -r requirements.txt

# mlx-whisper dichiara torch fra le dipendenze ma non lo importa mai (serve solo
# alla conversione dei checkpoint OpenAI, che non facciamo). Toglierlo = ~600MB in meno.
echo "==> Rimuovo pacchetti pesanti non usati (torch e derivati)"
pip uninstall -q -y torch sympy mpmath networkx || true
rm -rf .venv/lib/python*/site-packages/torch

echo "==> Scarico i modelli (una volta sola)"
python download_models.py

echo
echo "Pronto. Per l'uso quotidiano: doppio click su  start.command"
