#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/backend"

if [ ! -d .venv ]; then
  python3 -m venv .venv
fi

source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements.txt

if ! python -c "import cairo" >/dev/null 2>&1 && ! python -c "import cairocffi" >/dev/null 2>&1; then
  echo "Instalando dependencia de renderizacao do igraph..."
  python -m pip install pycairo || python -m pip install cairocffi
fi

python -m uvicorn app.main:app --reload --port 8000
