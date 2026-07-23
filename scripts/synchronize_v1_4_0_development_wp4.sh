#!/usr/bin/env bash
set -euo pipefail

repo="${1:-/workspaces/v0-osap-formal-core}"
cd "$repo"

expected_repository="olegovation-ship-it/v0-osap-formal-core"
expected_source_head="633c01e33271ffb17c045f69aa266a595ebc7e74"
closeout_marker="release/v1.4.0/GATE3_CLUSTER_B_WP4_POST_MERGE_ARCHIVAL_CLOSEOUT_RECORD.json"

test -z "$(git status --short)"
test "$(git branch --show-current)" = "v1.4.0-development"

origin_url="$(git remote get-url origin)"
case "$origin_url" in
  *"$expected_repository"*) ;;
  *) echo "FAIL: unexpected origin $origin_url" >&2; exit 1 ;;
esac

git fetch origin --prune

local_head="$(git rev-parse HEAD)"
remote_dev="$(git rev-parse origin/v1.4.0-development)"
remote_main="$(git rev-parse origin/main)"

test "$local_head" = "$remote_dev"
git merge-base --is-ancestor "$expected_source_head" "$remote_dev"
git merge-base --is-ancestor "$remote_dev" "$remote_main"
git cat-file -e "origin/main:$closeout_marker"

relation_before="$(git rev-list --left-right --count origin/main...origin/v1.4.0-development)"
main_ahead="$(printf '%s' "$relation_before" | awk '{print $1}')"
dev_ahead="$(printf '%s' "$relation_before" | awk '{print $2}')"
test "$main_ahead" -ge 1
test "$dev_ahead" -eq 0

git merge --ff-only origin/main
test -z "$(git status --short)"

git push origin v1.4.0-development
git fetch origin --prune

test "$(git rev-parse HEAD)" = "$(git rev-parse origin/main)"
test "$(git rev-parse HEAD)" = "$(git rev-parse origin/v1.4.0-development)"

relation_after="$(git rev-list --left-right --count origin/main...origin/v1.4.0-development)"
test "$relation_after" = $'0\t0' || test "$relation_after" = "0 0"

echo "PASS: WP4 post-closeout main/development fast-forward synchronization complete"
git log -5 --oneline --decorate
