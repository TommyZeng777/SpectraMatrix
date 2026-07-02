#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

PYTHON_BIN="${PYTHON_BIN:-python3}"

"$PYTHON_BIN" -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e "packages/spectral_core[npz,api]"
python script/generate_sample_csv.py --out datasets/sample_csv

cat <<'MSG'

SpectraMatrix quickstart is ready.

Start the workbench with:
  source .venv/bin/activate
  PYTHONPATH=packages/spectral_core/src spectral-api

Then open:
  http://127.0.0.1:8765/

Synthetic CSV files were generated under:
  datasets/sample_csv/

MSG
