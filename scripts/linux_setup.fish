#!/usr/bin/env fish
cd (dirname (status --current-filename))/..

python -m venv .venv

source .venv/bin/activate.fish

pip install -r requirements.txt
