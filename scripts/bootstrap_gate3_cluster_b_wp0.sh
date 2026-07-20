#!/usr/bin/env bash
set -euo pipefail

EXPECTED_REPO="olegovation-ship-it/v0-osap-formal-core"
BASE="a13a96fda4964dde1719c7d014f11878e1103b20"
TARGET="v1.4.0-development"
TAG_TARGET="13bf095688bcabd5b090f188e9bd28a16237edeb"

REPO_ROOT="$(git rev-parse --show-toplevel)"
cd "$REPO_ROOT"

REMOTE_URL="$(git remote get-url origin)"
case "$REMOTE_URL" in
  *"$EXPECTED_REPO"*) ;;
  *) echo "ERROR: unexpected origin: $REMOTE_URL" >&2; exit 2 ;;
esac

if ! git diff --quiet || ! git diff --cached --quiet; then
  echo "ERROR: tracked changes exist before bootstrap." >&2
  exit 2
fi

git fetch origin --tags --prune
OBSERVED_MAIN="$(git rev-parse origin/main)"
if [[ "$OBSERVED_MAIN" != "$BASE" ]]; then
  echo "ERROR: origin/main moved: $OBSERVED_MAIN" >&2
  exit 2
fi

OBSERVED_TAG="$(git rev-parse 'refs/tags/v1.3.0^{}')"
if [[ "$OBSERVED_TAG" != "$TAG_TARGET" ]]; then
  echo "ERROR: v1.3.0 tag target mismatch: $OBSERVED_TAG" >&2
  exit 2
fi

if git show-ref --verify --quiet "refs/heads/$TARGET"; then
  EXISTING="$(git rev-parse "$TARGET")"
  if [[ "$EXISTING" != "$BASE" ]]; then
    echo "ERROR: local $TARGET exists at $EXISTING, expected $BASE" >&2
    exit 2
  fi
  git switch "$TARGET"
elif git show-ref --verify --quiet "refs/remotes/origin/$TARGET"; then
  EXISTING="$(git rev-parse "origin/$TARGET")"
  if [[ "$EXISTING" != "$BASE" ]]; then
    echo "ERROR: remote $TARGET exists at $EXISTING, expected $BASE" >&2
    exit 2
  fi
  git switch -c "$TARGET" --track "origin/$TARGET"
else
  git switch -c "$TARGET" "$BASE"
fi

chmod +x scripts/bootstrap_gate3_cluster_b_wp0.sh scripts/verify_gate3_cluster_b_wp0.py
python scripts/verify_gate3_cluster_b_wp0.py --online

echo
echo "WP0 branch bootstrap PASS. Review and commit with:"
echo "  git add .github/workflows/gate3-cluster-b-wp0.yml docs/gate3/cluster_b release/v1.4.0 schemas/v1.4.0 scripts/bootstrap_gate3_cluster_b_wp0.sh scripts/verify_gate3_cluster_b_wp0.py tests/test_gate3_cluster_b_wp0.py"
echo "  git commit -m 'Gate 3 Cluster B WP0: freeze baseline and bootstrap v1.4.0 development'"
echo "  git push -u origin $TARGET"
