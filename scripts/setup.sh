#!/usr/bin/env bash
# One-command setup (PRD NFR-04): virtual environment, dependencies, and the spaCy language model
# that the PII redactor needs.
set -euo pipefail
cd "$(dirname "$0")/.."
PYTHON="${PYTHON:-$(command -v python3.12 || command -v python3)}"
"$PYTHON" -m venv .venv
.venv/bin/pip install -q --upgrade pip
.venv/bin/pip install -q -e ".[dev]"
.venv/bin/python -m spacy download en_core_web_sm
echo "Setup complete. Start the dashboard with: .venv/bin/streamlit run src/airg/dashboard/app.py"
