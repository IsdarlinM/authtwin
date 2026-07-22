#!/usr/bin/env sh
set -eu

PROJECT="AuthTwin"
CMD="authtwin"
INSTALL_ROOT="${HOME}/.authtwin"
VENV="$INSTALL_ROOT/venv"
BIN_DIR="${HOME}/.local/bin"
SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
REPO_ROOT=$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd)
CONSTRAINTS="$REPO_ROOT/requirements/runtime-py311.lock"

if [ "$(id -u)" = "0" ] && [ "${ALLOW_ROOT_INSTALL:-0}" != "1" ]; then
  echo "Refusing root install by default. Run as your normal user or set ALLOW_ROOT_INSTALL=1 intentionally." >&2
  exit 2
fi

PYTHON="${PYTHON:-python3}"
"$PYTHON" -c 'import sys; raise SystemExit(0 if sys.version_info >= (3,11) else 1)' || {
  echo "Python 3.11+ is required." >&2
  exit 2
}

mkdir -p "$INSTALL_ROOT" "$BIN_DIR"
if [ ! -x "$VENV/bin/python" ]; then
  "$PYTHON" -m venv "$VENV"
fi
"$VENV/bin/python" -m pip install --upgrade pip
SRIC_SOURCE="${SRIC_CORE_SOURCE:-}"
if [ -z "$SRIC_SOURCE" ] && [ -d "$REPO_ROOT/../sric-core" ]; then
  SRIC_SOURCE="$REPO_ROOT/../sric-core"
fi
if [ -n "$SRIC_SOURCE" ] && [ -f "$SRIC_SOURCE/pyproject.toml" ]; then
  "$VENV/bin/python" -m pip install --upgrade -c "$CONSTRAINTS" "$SRIC_SOURCE"
else
  if ! "$VENV/bin/python" -m pip install -c "$CONSTRAINTS" 'sric-core>=0.3,<0.4'; then
    echo "SRIC Core 0.3.x is required. Clone sric-core next to this repository or set SRIC_CORE_SOURCE=/path/to/sric-core." >&2
    exit 3
  fi
fi

"$VENV/bin/python" -m pip install --upgrade -c "$CONSTRAINTS" "$REPO_ROOT"
ln -sfn "$VENV/bin/$CMD" "$BIN_DIR/$CMD"

PROFILE="${HOME}/.profile"
PATH_LINE='export PATH="$HOME/.local/bin:$PATH"'
touch "$PROFILE"
if ! grep -F "$PATH_LINE" "$PROFILE" >/dev/null 2>&1; then
  printf '
# Security Research Intelligence tools
%s
' "$PATH_LINE" >> "$PROFILE"
fi

"$VENV/bin/$CMD" doctor
printf '%s installed successfully.
' "$PROJECT"
printf 'Command: %s
' "$CMD"
printf 'PATH is configured for new shells via %s.
' "$PROFILE"
