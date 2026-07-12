#!/bin/bash
# Quick health check — auth status + notebook listing
set -e

echo "═══ NotebookLM CLI smoke test ═══"

echo ""
echo "[1] which nlm:"
which nlm || { echo "  ✗ nlm not on PATH. Run install.sh first."; exit 1; }

echo ""
echo "[2] Auth status:"
nlm login --check 2>&1 | head -5

echo ""
echo "[3] Notebook list (first 5):"
nlm notebook list --json 2>/dev/null | head -50 || \
  nlm notebook list 2>&1 | head -20

echo ""
echo "[4] Doctor:"
nlm doctor 2>&1 | head -20

echo ""
echo "═══ Done ═══"
