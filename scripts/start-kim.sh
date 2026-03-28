#!/bin/bash
# Start Kim Wexler agent
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "$(date): Kim starting..." >> /tmp/kim-debug.log
cd "$PROJECT_DIR"
echo "$(date): cwd=$(pwd)" >> /tmp/kim-debug.log
echo "$(date): node=$(node --version)" >> /tmp/kim-debug.log
exec node dist/index.js --agent kim
