#!/bin/bash
# Stage src/, user-docs/, examples/, and the app icon into
# packaging/deb/opt/leopard/ ahead of `dpkg-deb --build packaging/deb`.
#
# packaging/deb/opt/leopard/ is regenerated from the repository source on
# every run rather than hand-copied, so the .deb can't silently drift from
# src/leopard_lang and src/leopard_ide the way the old packaging/ide-src
# copy did.
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"
STAGE="$SCRIPT_DIR/deb/opt/leopard"

echo "Staging $STAGE from $REPO_ROOT ..."

rm -rf "$STAGE"
mkdir -p "$STAGE"

cp -r "$REPO_ROOT/src" "$STAGE/src"
cp -r "$REPO_ROOT/user-docs" "$STAGE/user-docs"
cp -r "$REPO_ROOT/examples" "$STAGE/examples"
cp "$REPO_ROOT/leopard-icon.svg" "$STAGE/leopard-icon.svg"

find "$STAGE" -name "__pycache__" -type d -prune -exec rm -rf {} +
find "$STAGE" -name "*.egg-info" -type d -prune -exec rm -rf {} +

echo "Staged."
