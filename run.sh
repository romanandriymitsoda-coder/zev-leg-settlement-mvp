#!/usr/bin/env bash
set -euo pipefail

# Run the ZEV/LEG MVP end-to-end on macOS/Linux.
# Creates .venv if missing, installs requirements, and runs the main script.

cd "$(dirname "$0")"

# Prefer python3 if available, otherwise fall back to python.
PYTHON=${PYTHON:-python3}
if ! command -v "$PYTHON" >/dev/null 2>&1; then
  PYTHON=python
fi

if [ ! -d ".venv" ]; then
  "$PYTHON" -m venv .venv
fi

# shellcheck disable=SC1091
source .venv/bin/activate

pip install -r requirements.txt

python scripts/run_mvp.py

# Copy latest figures to docs/ for GitHub visibility
mkdir -p docs
cp outputs/graph1_bill_change.png docs/graph1_bill_change.png
cp outputs/graph2_fairness_frontier.png docs/graph2_fairness_frontier.png
