from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
VERIFIER_PATH = ROOT / "release/v1.4.0/tools/verify_wp6_four_root_corrective_layer.py"
spec = importlib.util.spec_from_file_location("wp6_four_root_verifier", VERIFIER_PATH)
assert spec and spec.loader
MODULE = importlib.util.module_from_spec(spec)
spec.loader.exec_module(MODULE)


def manifest() -> dict:
    return MODULE.load_manifest(ROOT)


def provider(path: str) -> bytes:
    base = Path(os.environ["V0_OSAP_PREDECESSOR_BLOB_DIR"])
    return (base / path).read_bytes()


def fail_marker(fn, marker: str) -> None:
    with pytest.raises(RuntimeError, match=marker):
        fn()


def test_positive_manifest_validation() -> None:
    MODULE.validate_manifest(manifest())


def test_positive_transformation_derivation() -> None:
    actual = MODULE.transformed_modified_bytes(manifest(), provider)
    assert sorted(actual) == MODULE.MODIFIED_PATHS
    for path, data in actual.items():
        assert data == (ROOT / path).read_bytes()


def test_positive_ledger_verification() -> None:
    rows = MODULE.validate_ledger(ROOT)
    assert len(rows) == 4
    assert MODULE.LEDGER not in [path for _, path in rows]


def test_positive_four_root_matrix() -> None:
    result = MODULE.verify_four_root_matrix(ROOT)
    assert result["status"] == "PASS"
    assert result["root_coverage"] == "COMPLETE"


def test_positive_cli_combinations() -> None:
    env = os.environ.copy()
    env["V0_OSAP_PACKAGE_ONLY"] = "1"
    matrix = subprocess.run([sys.executable, str(VERIFIER_PATH), "--mode", "committed", "--verify-four-root-matrix"], cwd=ROOT, env=env, capture_output=True, text=True)
    assert matrix.returncode == 0, matrix.stdout + matrix.stderr
    for workflow, group in MODULE.EXPECTED_REPLAY_GROUPS.items():
        for job in group["jobs"]:
            cp = subprocess.run([sys.executable, str(VERIFIER_PATH), "--mode", "committed", "--replay-workflow", workflow, "--job", job], cwd=ROOT, env=env, capture_output=True, text=True)
            assert cp.returncode == 0, cp.stdout + cp.stderr


def test_replay_harness_uses_detached_git_worktree(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    anchor = "a" * 40
    repository = tmp_path / "repository"
    repository.mkdir()
    events: list[tuple[str, tuple[str, ...], Path | None]] = []
    linked_worktree: Path | None = None

    def completed(args: tuple[str, ...], text: bool) -> subprocess.CompletedProcess:
        return subprocess.CompletedProcess(args, 0, stdout="" if text else b"", stderr="" if text else b"")

    def fake_require(*args: str, cwd: Path | None = None, env=None, text: bool = True):
        nonlocal linked_worktree
        events.append(("require", args, cwd))
        if args[:4] == ("git", "worktree", "add", "--detach"):
            linked_worktree = Path(args[4])
            linked_worktree.mkdir(parents=True)
            (linked_worktree / ".git").write_text("gitdir: synthetic\n", encoding="utf-8")
        return completed(args, text)

    def fake_run(*args: str, cwd: Path | None = None, env=None, text: bool = True):
        events.append(("run", args, cwd))
        if args[:4] == ("git", "worktree", "remove", "--force"):
            assert linked_worktree is not None
            assert Path(args[4]) == linked_worktree
            return completed(args, text)
        assert linked_worktree is not None
        assert cwd == linked_worktree
        assert (linked_worktree / ".git").is_file()
        return completed(args, text)

    monkeypatch.setattr(MODULE, "ROOT", repository)
    monkeypatch.setattr(MODULE, "require", fake_require)
    monkeypatch.setattr(MODULE, "run", fake_run)

    result = MODULE.execute_phase(anchor, [["python", "synthetic_child.py"]], False)
    assert result == [{"command": ["python", "synthetic_child.py"], "return_code": 0}]
    assert any(event[1][:4] == ("git", "worktree", "add", "--detach") for event in events)
    assert any(event[1][:4] == ("git", "worktree", "remove", "--force") for event in events)


def test_modified_surface_mismatch() -> None:
    expected = MODULE.transformed_modified_bytes(manifest(), provider)
    bad_root = ROOT.parent / "bad-modified-surface"
    if bad_root.exists():
        import shutil; shutil.rmtree(bad_root)
    import shutil; shutil.copytree(ROOT, bad_root)
    path = MODULE.SUCCESSOR_ATTESTATION
    (bad_root / path).write_bytes(expected[path] + b"# unexpected\n")
    fail_marker(lambda: MODULE.validate_modified_surface(manifest(), bad_root, provider), "MODIFIED_SURFACE_MISMATCH")
    shutil.rmtree(bad_root)


def test_additive_predecessor_presence_failure() -> None:
    base = Path(os.environ["V0_OSAP_PREDECESSOR_BLOB_DIR"])
    target = base / MODULE.WORKFLOW
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("unexpected\n", encoding="utf-8")
    try:
        fail_marker(MODULE.validate_additive_predecessor_absence, "ADDITIVE_PREDECESSOR_PRESENCE")
    finally:
        target.unlink()


def test_missing_transformation_failure() -> None:
    value = manifest(); value["transformations"] = value["transformations"][:2]
    fail_marker(lambda: MODULE.validate_manifest(value), "MANIFEST_TRANSFORMATION_COUNT_FAILURE")


def test_non_unique_replacement_failure() -> None:
    value = manifest(); item = value["transformations"][0]["replacements"][0]
    item["old"] = "          "
    item["old_sha256"] = MODULE.sha256_bytes(item["old"].encode("utf-8"))
    fail_marker(lambda: MODULE.transformed_modified_bytes(value, provider), "NON_UNIQUE_REPLACEMENT")


def test_predecessor_blob_mismatch() -> None:
    value = manifest(); value["transformations"][0]["predecessor_blob_sha1"] = "0" * 40
    fail_marker(lambda: MODULE.transformed_modified_bytes(value, provider), "PREDECESSOR_BLOB_MISMATCH")


def test_old_digest_mismatch() -> None:
    value = manifest(); value["transformations"][0]["replacements"][0]["old_sha256"] = "0" * 64
    fail_marker(lambda: MODULE.transformed_modified_bytes(value, provider), "OLD_SHA256_FAILURE")


def test_new_digest_mismatch() -> None:
    value = manifest(); value["transformations"][0]["replacements"][0]["new_sha256"] = "0" * 64
    fail_marker(lambda: MODULE.transformed_modified_bytes(value, provider), "NEW_SHA256_FAILURE")


def test_ledger_self_inclusion_failure() -> None:
    import shutil
    bad_root = ROOT.parent / "bad-ledger-self"
    if bad_root.exists(): shutil.rmtree(bad_root)
    shutil.copytree(ROOT, bad_root)
    rows = MODULE.parse_ledger_bytes((bad_root / MODULE.LEDGER).read_bytes())
    rows[-1] = (rows[-1][0], MODULE.LEDGER)
    (bad_root / MODULE.LEDGER).write_bytes("".join(f"{d}  {p}\n" for d, p in rows).encode())
    fail_marker(lambda: MODULE.validate_ledger(bad_root), "LEDGER_SELF_EXCLUSION_OR_ORDER_FAILURE")
    shutil.rmtree(bad_root)


def test_ledger_entry_count_failure() -> None:
    import shutil
    bad_root = ROOT.parent / "bad-ledger-count"
    if bad_root.exists(): shutil.rmtree(bad_root)
    shutil.copytree(ROOT, bad_root)
    rows = MODULE.parse_ledger_bytes((bad_root / MODULE.LEDGER).read_bytes())[:3]
    (bad_root / MODULE.LEDGER).write_bytes("".join(f"{d}  {p}\n" for d, p in rows).encode())
    fail_marker(lambda: MODULE.validate_ledger(bad_root), "LEDGER_ENTRY_COUNT_FAILURE")
    shutil.rmtree(bad_root)


def test_root_coverage_failure() -> None:
    value = manifest(); value["root_coverage"]["ROOT_4"]["status"] = "INCOMPLETE"
    fail_marker(lambda: MODULE.validate_manifest(value), "ROOT_COVERAGE_STATUS_FAILURE")


def test_replay_command_omission() -> None:
    original = copy.deepcopy(MODULE.EXPECTED_REPLAY_GROUPS)
    MODULE.EXPECTED_REPLAY_GROUPS["wp6-audit"]["jobs"]["replay-claims"]["commands"] = []
    try:
        fail_marker(lambda: MODULE.replay_job("wp6-audit", "replay-claims", execute=False), "REPLAY_COMMAND_OMISSION")
    finally:
        MODULE.EXPECTED_REPLAY_GROUPS.clear(); MODULE.EXPECTED_REPLAY_GROUPS.update(original)


def test_invalid_workflow_job_combination() -> None:
    fail_marker(lambda: MODULE.replay_job("wp6-audit", "replay-matrix", execute=False), "INVALID_WORKFLOW_JOB_COMBINATION")


def test_immutable_repository_state_checks() -> None:
    before = MODULE.repository_snapshot(ROOT)
    MODULE.verify_four_root_matrix(ROOT)
    after = MODULE.repository_snapshot(ROOT)
    assert before == after
