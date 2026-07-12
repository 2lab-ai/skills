#!/bin/bash
# Shorts skill — wrapper script
# Usage: run.sh <command> [options]
# Commands: run, draft, produce, upload, topics, niches
#
# Examples:
#   run.sh run --news "Elon Musk AI" --niche tech --lang en
#   run.sh draft --news "headline" --niche tech
#   run.sh topics --niche tech --limit 10
#   run.sh niches

set -euo pipefail

SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"
VENV="$SKILL_DIR/.venv"

if [ ! -d "$VENV" ]; then
    echo "Error: venv not found at $VENV"
    echo "Run: python3 -m venv $VENV && $VENV/bin/pip install -r $SKILL_DIR/requirements.txt"
    exit 1
fi

source "$VENV/bin/activate"
cd "$SKILL_DIR"

exec python -m verticals "$@"
