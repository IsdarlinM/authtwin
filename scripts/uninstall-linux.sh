#!/usr/bin/env sh
set -eu
INSTALL_ROOT="${HOME}/.authtwin"
BIN="${HOME}/.local/bin/authtwin"
rm -f "$BIN"
rm -rf "$INSTALL_ROOT"
echo "Removed AuthTwin. User-created workspaces outside $INSTALL_ROOT were not touched."
