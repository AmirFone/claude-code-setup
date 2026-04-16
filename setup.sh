#!/usr/bin/env bash
set -euo pipefail

CLAUDE_DIR="$HOME/.claude"
REPO_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "Setting up Claude Code config from $REPO_DIR"

# Core config files
cp "$REPO_DIR/CLAUDE.md" "$CLAUDE_DIR/CLAUDE.md"
cp "$REPO_DIR/settings.json" "$CLAUDE_DIR/settings.json"
if [ -f "$REPO_DIR/settings.local.json" ]; then
  cp "$REPO_DIR/settings.local.json" "$CLAUDE_DIR/settings.local.json"
fi

# Hooks
mkdir -p "$CLAUDE_DIR/hooks/lib" "$CLAUDE_DIR/hooks/utils/llm" "$CLAUDE_DIR/hooks/utils/tts"
rsync -av --exclude='__pycache__' "$REPO_DIR/hooks/" "$CLAUDE_DIR/hooks/"

# Rules
mkdir -p "$CLAUDE_DIR/rules"
rsync -av "$REPO_DIR/rules/" "$CLAUDE_DIR/rules/"

# Agents
mkdir -p "$CLAUDE_DIR/agents"
rsync -av "$REPO_DIR/agents/" "$CLAUDE_DIR/agents/"

# Commands
mkdir -p "$CLAUDE_DIR/commands"
rsync -av "$REPO_DIR/commands/" "$CLAUDE_DIR/commands/"

# Skills
mkdir -p "$CLAUDE_DIR/skills"
rsync -av --exclude='__pycache__' "$REPO_DIR/skills/" "$CLAUDE_DIR/skills/"

# Install plugins from marketplaces
echo ""
echo "Installing plugins..."

install_plugin() {
  local marketplace="$1"
  local plugin="$2"
  echo "  Installing $plugin from $marketplace..."
  claude plugin install "$plugin" --marketplace "$marketplace" 2>/dev/null || \
    echo "    (manual install may be needed for $plugin)"
}

if command -v claude &> /dev/null; then
  # Add marketplaces
  claude plugin marketplace add anthropics/claude-code 2>/dev/null || true
  claude plugin marketplace add anthropics/claude-plugins-official 2>/dev/null || true
  claude plugin marketplace add jarrodwatts/claude-hud 2>/dev/null || true

  # Install each plugin
  install_plugin "claude-code-plugins" "frontend-design"
  install_plugin "claude-plugins-official" "ralph-wiggum"
  install_plugin "claude-hud" "claude-hud"
  install_plugin "claude-code-plugins" "ralph-wiggum"
  install_plugin "claude-plugins-official" "playwright"
  install_plugin "claude-plugins-official" "rust-analyzer-lsp"
else
  echo "  'claude' CLI not found. Install plugins manually after installing Claude Code."
  echo "  Plugins to install:"
  echo "    - frontend-design (anthropics/claude-code)"
  echo "    - ralph-wiggum (anthropics/claude-plugins-official)"
  echo "    - claude-hud (jarrodwatts/claude-hud)"
  echo "    - ralph-wiggum (anthropics/claude-code)"
  echo "    - playwright (anthropics/claude-plugins-official)"
  echo "    - rust-analyzer-lsp (anthropics/claude-plugins-official)"
fi

echo ""
echo "Done. Restart Claude Code to pick up changes."
