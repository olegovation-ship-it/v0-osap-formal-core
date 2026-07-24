#!/usr/bin/env bash
set -euo pipefail
repo="$(git rev-parse --show-toplevel)"
cd "$repo"

dry_run=false
case "${1:-}" in
  "") ;;
  --dry-run) dry_run=true ;;
  *) echo "Usage: $0 [--dry-run]" >&2; exit 2 ;;
esac

test "$(git branch --show-current)" = "v1.4.0-development"
test -z "$(git status --porcelain)"
git fetch origin --prune

main="$(git rev-parse origin/main)"
dev="$(git rev-parse origin/v1.4.0-development)"
read -r main_ahead development_ahead < <(
  git rev-list --left-right --count origin/main...origin/v1.4.0-development
)

classification="$(
  python scripts/classify_v1_4_0_development_sync_relation_wp5.py     --main-ahead "$main_ahead"     --development-ahead "$development_ahead"     --format shell
)" || {
  printf '%s\n' "$classification"
  echo "Refusing unsafe development synchronization relation" >&2
  exit 1
}
printf '%s\n' "$classification"
decision="$(printf '%s\n' "$classification" | sed -n 's/^DECISION=//p')"

if [ "$decision" = "ALREADY_SYNCHRONIZED" ]; then
  test "$main" = "$dev"
  test "$(git rev-parse HEAD)" = "$dev"
  echo "WP5 DEVELOPMENT SYNCHRONIZATION: ALREADY SYNCHRONIZED"
  exit 0
fi

test "$decision" = "FAST_FORWARD_ALLOWED"
git merge-base --is-ancestor "$dev" "$main"

if [ "$dry_run" = true ]; then
  echo "WP5 DEVELOPMENT SYNCHRONIZATION DRY-RUN: PASS"
  exit 0
fi

git merge --ff-only origin/main
git push origin v1.4.0-development
git fetch origin --prune
test "$(git rev-parse HEAD)" = "$(git rev-parse origin/main)"
test "$(git rev-parse HEAD)" = "$(git rev-parse origin/v1.4.0-development)"
test -z "$(git status --porcelain)"
echo "WP5 DEVELOPMENT SYNCHRONIZATION: PASS"
