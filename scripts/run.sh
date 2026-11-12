#!/bin/bash
set -e
cd "$(dirname "$0")/.."
python -m app.seed
uvicorn app.main:app --reload --port 8000
