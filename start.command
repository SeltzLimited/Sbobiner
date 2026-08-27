#!/usr/bin/env bash
# Uso quotidiano. Doppio click da Finder. Funziona offline.
cd "$(dirname "$0")"
source .venv/bin/activate
exec python app.py
