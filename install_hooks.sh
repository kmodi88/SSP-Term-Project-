#!/usr/bin/env bash
# install_hooks.sh
# Run once after cloning: bash install_hooks.sh
# This installs a git hook so that `git status` automatically runs all tests.

HOOK_SRC="scripts/pre-status-hook"
HOOK_DST=".git/hooks/pre-status"

if [ ! -d ".git" ]; then
  echo "ERROR: Run this script from the root of the git repository."
  exit 1
fi

cp "$HOOK_SRC" "$HOOK_DST"
chmod +x "$HOOK_DST"
echo "✅  Git pre-status hook installed. Tests will run on every 'git status'."