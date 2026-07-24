#!/usr/bin/env bash
set -euo pipefail
repo="$(git rev-parse --show-toplevel)"
cd "$repo"
test "$(git branch --show-current)" = "v1.4.0-development"
test -z "$(git status --porcelain)"
git fetch origin --prune
main="$(git rev-parse origin/main)"
dev="$(git rev-parse origin/v1.4.0-development)"
case "$(git rev-list --left-right --count origin/main...origin/v1.4.0-development)" in
  "1"$'\t'"0"|"1 0") ;;
  "0"$'\t'"0"|"0 0") echo "Already synchronized"; exit 0 ;;
  *) echo "Refusing non-fast-forward or unexpected relation"; exit 1 ;;
esac
git merge-base --is-ancestor "$dev" "$main"
git merge --ff-only origin/main
git push origin v1.4.0-development
git fetch origin --prune
test "$(git rev-parse HEAD)" = "$(git rev-parse origin/main)"
test "$(git rev-parse HEAD)" = "$(git rev-parse origin/v1.4.0-development)"
test -z "$(git status --porcelain)"
echo "WP5 DEVELOPMENT SYNCHRONIZATION: PASS"
