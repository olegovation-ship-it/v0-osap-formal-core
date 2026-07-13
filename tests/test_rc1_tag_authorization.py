from __future__ import annotations

import subprocess
import sys

from scripts.rc1_release_closure_lib import forbidden_release_commands
from scripts.rc1_tag_release_lib import (
    AUTHORIZED_STATE,
    CANDIDATE_TAG,
    CLOSURE_MERGE_COMMIT,
    read_json,
    repository_root,
    sha256_file,
)

ROOT = repository_root()


def test_authorization_record_is_exact_target_and_nonreleasing() -> None:
    record = read_json(ROOT / "release/v1.3.0/RC1_TAG_AUTHORIZATION_RECORD.json")
    assert record["state"] == AUTHORIZED_STATE
    assert record["authorized_tag_name"] == CANDIDATE_TAG
    assert record["authorized_tag_target_commit"] == CLOSURE_MERGE_COMMIT
    assert record["authorization_is_target_specific"] is True
    assert record["release_actions"]["tag_target_authorized"] is True
    assert record["release_actions"]["rc1_tag_created"] is False
    assert record["release_actions"]["github_prerelease_created"] is False


def test_final_tag_message_is_not_draft() -> None:
    text = (ROOT / "release/v1.3.0/RC1_ANNOTATED_TAG_MESSAGE.txt").read_text(encoding="utf-8")
    assert text.startswith("V0 OSAP v1.3.0-rc1\n")
    assert CLOSURE_MERGE_COMMIT in text
    assert "DRAFT ONLY" not in text


def test_authorization_workflow_is_validation_only() -> None:
    text = (ROOT / ".github/workflows/rc1-tag-authorization.yml").read_text(encoding="utf-8")
    assert forbidden_release_commands(text) == []
    assert "create_rc1_annotated_tag.py" not in text
    assert "create_rc1_github_prerelease.py" not in text


def test_authorization_manifest_hashes_replay() -> None:
    manifest = read_json(ROOT / "release/v1.3.0/RC1_TAG_AUTHORIZATION_MANIFEST.json")
    assert manifest["authorized_tag_target_commit"] == CLOSURE_MERGE_COMMIT
    for rel_path, expected_hash in manifest["files"].items():
        assert sha256_file(ROOT / rel_path) == expected_hash


def test_tag_creation_script_is_dry_run_by_default() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/create_rc1_annotated_tag.py"],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    # A repository without fetched tags/remotes may refuse safely; it must never create a tag.
    assert result.returncode in {0, 1}
    assert "created annotated tag" not in result.stdout.lower()
