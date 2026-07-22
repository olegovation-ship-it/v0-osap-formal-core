#!/usr/bin/env bash
set -euo pipefail
repo="${1:-/workspaces/v0-osap-formal-core}"
cd "$repo"
git fetch origin --prune
git switch main
git pull --ff-only origin main
git switch v1.4.0-development
git merge --ff-only origin/main
git push origin v1.4.0-development
test -z "$(git status --short)"
relation="$(git rev-list --left-right --count origin/main...origin/v1.4.0-development)"
test "$relation" = $'0\t0' || test "$relation" = "0 0"
echo "PASS: WP2 post-closeout main/development fast-forward synchronization complete"
git log -5 --oneline --decorate
