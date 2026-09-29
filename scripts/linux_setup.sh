#!/bin/bash
cd "$(dirname "$0")/.."

python -m venv .venv

source .venv/bin/activate

pip install -r requirements.txt
