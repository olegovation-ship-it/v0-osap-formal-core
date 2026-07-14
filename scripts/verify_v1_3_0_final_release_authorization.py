from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path

from v1_3_0_final_release_authorization_lib import (
    EXPECTED_STATE,
    FINAL_TAG,
    FINAL_TARGET,
    IMMUTABLE_DOI,
    IMMUTABLE_TAG,
    IMMUTABLE_TARGET,
    RC1_TAG,
    RC1_TARGET,
    assert_target_is_ancestor,
    git,
    tag_exists,
    tag_target,
)

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = "80911df7aacdac7ff411b49dcced161b98ac2071"
MANIFEST_REL = (
    "release/v1.3.0/"
    "V1_3_0_FINAL_RELEASE_AUTHORIZATION_MANIFEST.json"
)

def historical_blob(rel_path: str) -> bytes:
    return subprocess.run(
        ["git", "show", f"{SNAPSHOT}:{rel_path}"],
        cwd=ROOT,
        check=True,
        capture_output=True,
    ).stdout

def historical_json(rel_path: str):
    return json.loads(historical_blob(rel_path).decode("utf-8"))

def historical_text(rel_path: str) -> str:
    return historical_blob(rel_path).decode("utf-8")

parser = argparse.ArgumentParser()
parser.add_argument("--require-tags", action="store_true")
parser.add_argument("--allow-stable-tag-created", action="store_true")
args = parser.parse_args()

record = historical_json(
    "release/v1.3.0/V1_3_0_FINAL_RELEASE_AUTHORIZATION_RECORD.json"
)
manifest = historical_json(MANIFEST_REL)
metadata = historical_json(
    "release/v1.3.0/V1_3_0_GITHUB_FINAL_RELEASE_METADATA.json"
)

assert record["human_state"] == EXPECTED_STATE
assert record["stable_target"]["tag_name"] == FINAL_TAG
assert record["stable_target"]["target_commit"] == FINAL_TARGET
assert record["release_actions"]["stable_tag_created"] is False
assert record["release_actions"]["github_final_release_created"] is False
assert record["release_actions"]["zenodo_version_authorized"] is False
assert record["candidate_scope"]["conditional_theorems"] == [
    "T140",
    "T150",
    "T156",
]
assert record["candidate_scope"]["checker_component_version"] == "0.7.0.dev1"

for rel_path, expected in manifest["files"].items():
    actual = hashlib.sha256(historical_blob(rel_path)).hexdigest()
    assert actual == expected, rel_path

assert metadata["tagName"] == FINAL_TAG
assert metadata["targetCommit"] == FINAL_TARGET
assert metadata["isDraft"] is False
assert metadata["isPrerelease"] is False
assert metadata["makeLatest"] is True

assert_target_is_ancestor()
if args.require_tags:
    assert tag_exists(RC1_TAG) and tag_target(RC1_TAG) == RC1_TARGET
    assert tag_exists(IMMUTABLE_TAG) and tag_target(IMMUTABLE_TAG) == IMMUTABLE_TARGET

stable_exists = tag_exists(FINAL_TAG)
if args.allow_stable_tag_created:
    assert stable_exists and tag_target(FINAL_TAG) == FINAL_TARGET
    assert git("cat-file", "-t", f"refs/tags/{FINAL_TAG}") == "tag"
else:
    assert not stable_exists, f"{FINAL_TAG} already exists"

for rel_path in ("README.md", "docs/status_and_nonclaims.md"):
    text = historical_text(rel_path)
    assert EXPECTED_STATE in text
    assert FINAL_TARGET in text
    assert "0.7.0.dev1" in text
    assert IMMUTABLE_DOI in text

assert 'version = "0.7.0.dev1"' in historical_text("pyproject.toml")
workflow = historical_text(
    ".github/workflows/v1-3-0-final-release-authorization.yml"
)
for forbidden in ("git tag ", "gh release create", "--execute"):
    assert forbidden not in workflow, forbidden

print(
    "PASS: historical V0 OSAP v1.3.0 final-release authorization "
    "snapshot is preserved; exact stable-tag creation is permitted "
    "or observed only when explicitly allowed."
)
