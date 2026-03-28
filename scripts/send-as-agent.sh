#!/bin/bash
# Send a Telegram message FROM a specific agent's bot + log to hive_mind.
# Usage: send-as-agent.sh <agent_id> "message text" [action]
#
# Supported agents: tuco, lalo, gale, main (Nacho)
# Reads bot tokens from .env in the project root.
# Logs every message to hive_mind SQLite table for audit trail.
#
# Actions (optional, auto-detected from message):
#   task_accepted, task_completed, task_failed, task_progress
#
# Examples:
#   send-as-agent.sh tuco "📋 Принял задачу от Начо: поиск новостей"
#   send-as-agent.sh lalo "✅ Задача выполнена! Отправляю результат → Начо"
#   send-as-agent.sh gale "⏳ Работаю над задачей..."

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="$SCRIPT_DIR/../.env"
DB_FILE="$SCRIPT_DIR/../store/claudeclaw.db"

if [ ! -f "$ENV_FILE" ]; then
  echo "send-as-agent.sh: .env not found at $ENV_FILE" >&2
  exit 1
fi

AGENT_ID="$1"
MESSAGE="$2"
ACTION="$3"

if [ -z "$AGENT_ID" ] || [ -z "$MESSAGE" ]; then
  echo "Usage: send-as-agent.sh <agent_id> \"message\" [action]" >&2
  echo "Agents: tuco, lalo, gale, main" >&2
  exit 1
fi

# Map agent_id to token env var
case "$AGENT_ID" in
  tuco)   TOKEN_VAR="TUCO_BOT_TOKEN" ;;
  lalo)   TOKEN_VAR="LALO_BOT_TOKEN" ;;
  gale)   TOKEN_VAR="GALE_BOT_TOKEN" ;;
  main)   TOKEN_VAR="TELEGRAM_BOT_TOKEN" ;;
  *)
    echo "send-as-agent.sh: Unknown agent '$AGENT_ID'. Use: tuco, lalo, gale, main" >&2
    exit 1
    ;;
esac

TOKEN=$(grep -E "^${TOKEN_VAR}=" "$ENV_FILE" | cut -d'=' -f2- | tr -d '"' | tr -d "'")
CHAT_ID=$(grep -E '^ALLOWED_CHAT_ID=' "$ENV_FILE" | cut -d'=' -f2- | tr -d '"' | tr -d "'")

if [ -z "$TOKEN" ]; then
  echo "send-as-agent.sh: $TOKEN_VAR not found in .env" >&2
  exit 1
fi

if [ -z "$CHAT_ID" ]; then
  echo "send-as-agent.sh: ALLOWED_CHAT_ID not found in .env" >&2
  exit 1
fi

# Auto-detect action from message if not provided
if [ -z "$ACTION" ]; then
  case "$MESSAGE" in
    *"Принял задачу"*|*"📋"*)  ACTION="task_accepted" ;;
    *"Задача выполнена"*|*"✅"*|*"Готово"*|*"готов"*)  ACTION="task_completed" ;;
    *"Ошибка"*|*"❌"*|*"Таймаут"*)  ACTION="task_failed" ;;
    *"Работаю"*|*"⏳"*|*"Получил данные"*)  ACTION="task_progress" ;;
    *)  ACTION="agent_message" ;;
  esac
fi

# 1. Send to Telegram
curl -s -X POST "https://api.telegram.org/bot${TOKEN}/sendMessage" \
  -d chat_id="${CHAT_ID}" \
  -d text="${MESSAGE}" > /dev/null

# 2. Log to hive_mind (if DB exists)
if [ -f "$DB_FILE" ]; then
  NOW=$(date +%s)
  # Escape single quotes in message for SQL
  SAFE_MSG=$(echo "$MESSAGE" | sed "s/'/''/g")
  sqlite3 "$DB_FILE" "INSERT INTO hive_mind (agent_id, chat_id, action, summary, artifacts, created_at) VALUES ('$AGENT_ID', '$CHAT_ID', '$ACTION', '${SAFE_MSG}', NULL, $NOW);" 2>/dev/null
fi

# 3. Update task board (board.md)
BOARD_SCRIPT="$SCRIPT_DIR/board-update.sh"
if [ -x "$BOARD_SCRIPT" ]; then
  # Extract task description (strip emoji prefixes for clean board entry)
  TASK_DESC=$(echo "$MESSAGE" | sed 's/^[📋✅❌⏳🔥🕵️🧪🐍🧪🔄 ]*//' | head -c 80)
  case "$ACTION" in
    task_accepted)  "$BOARD_SCRIPT" "$AGENT_ID" accepted "$TASK_DESC" ;;
    task_completed) "$BOARD_SCRIPT" "$AGENT_ID" done "$TASK_DESC" ;;
    task_failed)    "$BOARD_SCRIPT" "$AGENT_ID" error "$TASK_DESC" ;;
    task_progress)  "$BOARD_SCRIPT" "$AGENT_ID" working "$TASK_DESC" ;;
  esac
fi
