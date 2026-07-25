#!/usr/bin/env bash
set -euo pipefail
repo="$(git rev-parse --show-toplevel)"
cd "$repo"
mode="${1:---dry-run}"
token="${2:-}"
case "$mode" in
  --dry-run) ;;
  --execute)
    test "$token" = "I_AUTHORIZE_WP6_DEVELOPMENT_FAST_FORWARD" || { echo "Explicit synchronization authorization token missing" >&2; exit 2; }
    ;;
  *) echo "Usage: $0 [--dry-run | --execute I_AUTHORIZE_WP6_DEVELOPMENT_FAST_FORWARD]" >&2; exit 2 ;;
esac

test "$(git branch --show-current)" = "v1.4.0-development"
test -z "$(git status --porcelain)"
git fetch origin --prune
main="$(git rev-parse origin/main)"
dev="$(git rev-parse origin/v1.4.0-development)"
git merge-base --is-ancestor f984b59cec832307bac7270c7d437a789bec99ce "$main"
read -r main_ahead development_ahead < <(git rev-list --left-right --count origin/main...origin/v1.4.0-development)
classification="$(python scripts/classify_v1_4_0_development_sync_relation_wp6.py --main-ahead "$main_ahead" --development-ahead "$development_ahead" --format shell)" || { printf '%s
' "$classification"; echo "Refusing unsafe development synchronization relation" >&2; exit 1; }
printf '%s
' "$classification"
decision="$(printf '%s
' "$classification" | sed -n 's/^DECISION=//p')"
if [ "$decision" = "ALREADY_SYNCHRONIZED" ]; then
  test "$main" = "$dev"; test "$(git rev-parse HEAD)" = "$dev"
  echo "WP6 DEVELOPMENT SYNCHRONIZATION: ALREADY SYNCHRONIZED"; exit 0
fi
test "$decision" = "FAST_FORWARD_ALLOWED"
git merge-base --is-ancestor "$dev" "$main"
if [ "$mode" = "--dry-run" ]; then
  echo "WP6 DEVELOPMENT SYNCHRONIZATION DRY-RUN: PASS"; exit 0
fi
git merge --ff-only origin/main
git push origin v1.4.0-development
git fetch origin --prune
test "$(git rev-parse HEAD)" = "$(git rev-parse origin/main)"
test "$(git rev-parse HEAD)" = "$(git rev-parse origin/v1.4.0-development)"
test -z "$(git status --porcelain)"
echo "WP6 DEVELOPMENT SYNCHRONIZATION: PASS"
