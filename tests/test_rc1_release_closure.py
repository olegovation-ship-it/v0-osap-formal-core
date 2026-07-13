from __future__ import annotations

from pathlib import Path

from scripts.rc1_release_closure_lib import (
    expected_theorem_ids,
    forbidden_release_commands,
    read_json,
    repository_root,
    sha256_file,
)

ROOT = repository_root()


def test_rc1_expected_theorem_range_is_exact() -> None:
    ids = expected_theorem_ids()
    assert len(ids) == 36
    assert ids[0] == "T121"
    assert ids[-1] == "T156"


def test_rc1_tag_preparation_record_is_nonreleasing() -> None:
    record = read_json(ROOT / "release/v1.3.0/RC1_TAG_PREPARATION_RECORD.json")
    assert record["tag_target_commit"] is None
    assert record["conditional_theorems"] == ["T140", "T150", "T156"]
    assert not any(record["release_actions"].values())


def test_rc1_closure_workflow_contains_no_release_command() -> None:
    workflow = (ROOT / ".github/workflows/rc1-release-closure.yml").read_text(encoding="utf-8")
    assert forbidden_release_commands(workflow) == []
    assert "python -m pytest -q" in workflow
    assert "fetch-depth: 0" in workflow


def test_rc1_closure_manifest_hashes_replay() -> None:
    manifest = read_json(ROOT / "release/v1.3.0/RC1_RELEASE_CLOSURE_MANIFEST.json")
    for rel_path, expected_hash in manifest["files"].items():
        assert sha256_file(ROOT / rel_path) == expected_hash
