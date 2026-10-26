#!/usr/bin/env bash
# One-command setup (PRD NFR-04): virtual environment, dependencies, and the spaCy language model
# that the PII redactor needs.
set -euo pipefail
cd "$(dirname "$0")/.."
PYTHON="${PYTHON:-$(command -v python3.12 || command -v python3)}"
"$PYTHON" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)' || { echo "Python 3.11+ is required"; exit 1; }
"$PYTHON" -m venv .venv
.venv/bin/pip install -q --upgrade pip
.venv/bin/pip install -q -e ".[dev]"
.venv/bin/python -m spacy download en_core_web_sm
echo "Setup complete. Start the dashboard with: .venv/bin/streamlit run src/airg/dashboard/app.py"
