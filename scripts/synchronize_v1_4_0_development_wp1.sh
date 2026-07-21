#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
cd "$REPO_ROOT"
BRANCH="v1.4.0-development"
BASELINE="eaf142089230ea5a5096ae834bf4e733d5f369aa"
TAG_TARGET="13bf095688bcabd5b090f188e9bd28a16237edeb"

echo "===== WP1 CLOSEOUT FINAL BRANCH SYNCHRONIZATION ====="
git fetch origin --tags --prune

test "$(git branch --show-current)" = "$BRANCH" || { echo "ERROR: wrong branch"; exit 1; }
test -z "$(git status --porcelain)" || { echo "ERROR: worktree not clean"; exit 1; }
test "$(git rev-parse 'refs/tags/v1.3.0^{}')" = "$TAG_TARGET" || { echo "ERROR: frozen tag changed"; exit 1; }
MAIN="$(git rev-parse origin/main)"
DEV="$(git rev-parse origin/$BRANCH)"
git merge-base --is-ancestor "$BASELINE" "$MAIN" || { echo "ERROR: main lost canonical WP1 baseline"; exit 1; }
git merge-base --is-ancestor "$DEV" "$MAIN" || { echo "ERROR: development cannot fast-forward to main"; exit 1; }

git merge --ff-only origin/main
git push origin HEAD:refs/heads/$BRANCH
git fetch origin --prune

test "$(git rev-parse HEAD)" = "$(git rev-parse origin/main)"
test "$(git rev-parse origin/$BRANCH)" = "$(git rev-parse origin/main)"
test -z "$(git status --porcelain)"

echo "WP1_POST_MERGE_FINAL_SYNCHRONIZATION=PASS"
echo "canonical_wp1_baseline=$BASELINE"
echo "current_synchronized_tip=$(git rev-parse HEAD)"
echo "release_actions_authorized=false"
