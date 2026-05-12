#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/.venv"
LOG_DIR="${LOG_DIR:-$HOME/.telegram-crawler/logs}"

mkdir -p "$LOG_DIR"

if [ ! -d "$VENV_DIR" ]; then
    echo "Error: Virtual environment not found at $VENV_DIR"
    echo "Run: python3 -m venv .venv && source .venv/bin/activate && pip install -e '.[dev]'"
    exit 1
fi

source "$VENV_DIR/bin/activate"

LOG_FILE="$LOG_DIR/telegram-crawler-$(date +%Y-%m-%d).log"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Starting: telegram-crawler $*" >> "$LOG_FILE"

python -m telegram_crawler "$@" 2>&1 | while IFS= read -r line; do
    echo "$line"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $line" >> "$LOG_FILE"
done