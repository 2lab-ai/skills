#!/bin/bash
# notebooklm-mcp-cli installer + setup helper
# Idempotent: safe to re-run

set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "═══════════════════════════════════════════════════"
echo " NotebookLM MCP CLI — Install & Setup"
echo "═══════════════════════════════════════════════════"

# 1. Detect Python >= 3.11
PYV=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
echo "[1/5] Python detected: $PYV"
if ! python3 -c 'import sys; sys.exit(0 if sys.version_info >= (3,11) else 1)'; then
  echo "  ✗ Need Python ≥ 3.11. Got $PYV"
  exit 1
fi

# 2. Install via pipx (or uv if available)
echo "[2/5] Installing notebooklm-mcp-cli..."
if command -v uv >/dev/null 2>&1; then
  uv tool install --upgrade notebooklm-mcp-cli
elif command -v pipx >/dev/null 2>&1; then
  if pipx list 2>/dev/null | grep -q notebooklm-mcp-cli; then
    pipx upgrade notebooklm-mcp-cli
  else
    pipx install notebooklm-mcp-cli
  fi
else
  echo "  ✗ Neither uv nor pipx found. Install one first:"
  echo "      sudo apt install pipx   # or"
  echo "      curl -LsSf https://astral.sh/uv/install.sh | sh"
  exit 1
fi

# 3. Verify binaries on PATH
echo "[3/5] Verifying binaries..."
NLM=$(command -v nlm || true)
NLM_MCP=$(command -v notebooklm-mcp || true)
if [ -z "$NLM" ] || [ -z "$NLM_MCP" ]; then
  echo "  ⚠ Not on PATH. Run: pipx ensurepath  (then restart shell)"
  echo "     Or use directly: ~/.local/bin/nlm  /  ~/.local/bin/notebooklm-mcp"
else
  echo "  ✓ nlm:             $NLM"
  echo "  ✓ notebooklm-mcp:  $NLM_MCP"
fi

# 4. Auth check
echo "[4/5] Checking authentication..."
if nlm login --check 2>&1 | grep -qi "authenticated\|✓\|valid\|active"; then
  echo "  ✓ Already authenticated"
else
  echo "  ⚠ Not authenticated. Run: nlm login"
  echo "    (opens browser → login to Google → cookies captured)"
fi

# 5. Register MCP server with Claude Code (if claude CLI exists)
echo "[5/5] Claude Code MCP registration..."
if command -v claude >/dev/null 2>&1; then
  if claude mcp list 2>/dev/null | grep -q notebooklm-mcp; then
    echo "  ✓ Already registered with Claude Code"
  else
    echo "  ▸ Registering with Claude Code..."
    claude mcp add --scope user notebooklm-mcp notebooklm-mcp || \
      echo "    (manual: claude mcp add --scope user notebooklm-mcp notebooklm-mcp)"
  fi
else
  echo "  ℹ claude CLI not found. Register manually after install:"
  echo "      claude mcp add --scope user notebooklm-mcp notebooklm-mcp"
fi

echo ""
echo "═══════════════════════════════════════════════════"
echo " Setup complete. Next steps:"
echo "   1. nlm login                       # if not auth'd"
echo "   2. nlm notebook list               # smoke test"
echo "   3. (restart Claude Code if you registered MCP)"
echo "═══════════════════════════════════════════════════"
