#!/usr/bin/env bash
set -euo pipefail

UPSTREAM_URL="${CLAUDECLAW_UPSTREAM_URL:-https://github.com/earlyaidopters/claudeclaw.git}"
TARGET_DIR="${1:-runtime/claudeclaw}"
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if ! command -v git >/dev/null 2>&1; then
  echo "ERROR: git is required." >&2
  exit 1
fi

if ! command -v python3 >/dev/null 2>&1; then
  echo "ERROR: python3 is required." >&2
  exit 1
fi

TARGET_ABS="$(python3 -c 'import os,sys; print(os.path.abspath(sys.argv[1]))' "$TARGET_DIR")"

printf '\nClaudeClaw BANDA setup\n'
printf 'Upstream: %s\n' "$UPSTREAM_URL"
printf 'Runtime:  %s\n\n' "$TARGET_ABS"

if ! command -v git >/dev/null 2>&1; then
  echo "ERROR: git is required." >&2
  exit 1
fi

if [[ -e "$TARGET_ABS/.git" ]]; then
  if [[ -n "$(git -C "$TARGET_ABS" status --porcelain)" ]]; then
    echo "Runtime already exists and has local changes. Skipping upstream pull to avoid conflicts."
  else
    echo "Runtime already exists. Updating upstream checkout..."
    git -C "$TARGET_ABS" pull --ff-only
  fi
elif [[ -e "$TARGET_ABS" ]]; then
  echo "ERROR: target exists but is not a git checkout: $TARGET_ABS" >&2
  echo "Choose another path or remove the directory." >&2
  exit 1
else
  mkdir -p "$(dirname "$TARGET_ABS")"
  git clone "$UPSTREAM_URL" "$TARGET_ABS"
fi

copy_overlay_dir() {
  local src="$1"
  local dst="$2"
  mkdir -p "$dst"
  # Non-destructive by default: overwrite BANDA-managed files, but never delete
  # user-created agents, memory, task data, or local runtime files.
  if command -v rsync >/dev/null 2>&1; then
    rsync -a --backup --suffix=.banda.bak "$src"/ "$dst"/
  else
    cp -R "$src"/. "$dst"/
  fi
}

echo "Applying BANDA overlay..."
copy_overlay_dir "$ROOT_DIR/overlay/agents" "$TARGET_ABS/agents"
copy_overlay_dir "$ROOT_DIR/overlay/.claudeclaw" "$TARGET_ABS/.claudeclaw"
copy_overlay_dir "$ROOT_DIR/overlay/data" "$TARGET_ABS/data"
cp "$ROOT_DIR/overlay/CLAUDE.md.example" "$TARGET_ABS/CLAUDE.md.example"
cp "$ROOT_DIR/overlay/banner.txt" "$TARGET_ABS/banner.txt"
cp "$ROOT_DIR/.env.example" "$TARGET_ABS/.env.banda.example"

if [[ ! -f "$TARGET_ABS/.env" ]]; then
  cp "$ROOT_DIR/.env.example" "$TARGET_ABS/.env"
  echo "Created $TARGET_ABS/.env from BANDA template. Fill it with your own tokens before launch."
else
  echo "Kept existing $TARGET_ABS/.env unchanged. BANDA template copied to .env.banda.example."
fi

cat <<EOF

Done.

Next steps:
  cd "$TARGET_ABS"
  npm install
  cp .env.banda.example .env   # only if you want to reset env template
  # edit .env with your real Telegram bot tokens and chat ID
  npm run build
  npm start

Start sub-agents if upstream ClaudeClaw supports agent:start:
  npm run agent:start tuco
  npm run agent:start lalo
  npm run agent:start gale
  npm run agent:start kim

Note: upstream ClaudeClaw is cloned locally from:
  $UPSTREAM_URL
Its files are not redistributed by the BANDA repository.
Re-running setup is non-destructive: user-created runtime files are preserved,
and overwritten BANDA-managed files get a .banda.bak backup when rsync is available.
EOF
