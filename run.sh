#!/usr/bin/env bash
# run.sh
# Usage:
#   bash run.sh                          # runs all 9 input combinations
#   bash run.sh pdfs/cis-r1.pdf pdfs/cis-r2.pdf   # runs a single pair
#
# The script creates a Python venv, installs dependencies, and executes main.py.

set -e

VENV_DIR="comp5700-venv"
REQUIREMENTS="requirements.txt"

echo "  SSP Term Project — Automated Runner"

# 1. Create venv if it doesn't exist
if [ ! -d "$VENV_DIR" ]; then
  echo "[1/4] Creating virtual environment: $VENV_DIR"
  python3 -m venv "$VENV_DIR"
else
  echo "[1/4] Virtual environment already exists: $VENV_DIR"
fi

# 2. Activate venv
echo "[2/4] Activating virtual environment..."
source "$VENV_DIR/bin/activate"

# 3. Install requirements
echo "[3/4] Installing requirements..."
pip install --upgrade pip -q
pip install -r "$REQUIREMENTS" -q

# 4. Run main.py
echo "[4/4] Running main.py..."
if [ "$#" -eq 2 ]; then
  echo "  → Single pair: $1 and $2"
  python main.py "$1" "$2"
else
  echo "  → All 9 input combinations"
  python main.py
fi

echo ""
echo "✅  Done. Check the outputs/ and yamls/ directories for results."