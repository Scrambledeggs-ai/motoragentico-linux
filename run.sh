#!/bin/bash
cd "$(dirname "$0")"
exec ~/.local/bin/uv run streamlit run app.py "$@"
