#!/usr/bin/env bash
set -euo pipefail

if ! command -v python >/dev/null 2>&1; then
  echo "Python is not available on PATH." >&2
  exit 1
fi

python -m venv .venv

if [ -f ".venv/Scripts/activate" ]; then
  source ".venv/Scripts/activate"
else
  source ".venv/bin/activate"
fi

python -m pip install --upgrade pip
python -m pip install flask google-cloud-vision
python -m pip install -q -U google-genai

echo "Virtual environment ready in .venv"
echo "Activate with:"
echo "  source .venv/Scripts/activate   # Windows Git Bash"
echo "  source .venv/bin/activate       # macOS/Linux"
