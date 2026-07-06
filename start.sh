#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"
source /home/yotchi/mypy/bin/activate

python -u bot_controll.py
