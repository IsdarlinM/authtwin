#!/usr/bin/env sh
set -eu
INSTALL_ROOT="${HOME}/.authtwin"
BIN="${HOME}/.local/bin/authtwin"
rm -f "$BIN"
rm -rf "$INSTALL_ROOT/venv"
echo "Removed AuthTwin runtime. Workspaces, configuration and evidence under $INSTALL_ROOT were preserved."
