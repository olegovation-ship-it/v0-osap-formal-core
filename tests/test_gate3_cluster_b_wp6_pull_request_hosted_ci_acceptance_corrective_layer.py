from __future__ import annotations

import importlib.util
import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
VERIFIER_PATH = ROOT / "release/v1.4.0/tools/verify_wp6_pull_request_hosted_ci_acceptance_corrective_layer.py"
SPEC = importlib.util.spec_from_file_location("wp6_pr_ci_acceptance", VERIFIER_PATH)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def git(repo: Path, *args: str) -> str:
    completed = subprocess.run(["git", *args], cwd=repo, capture_output=True, text=True, check=True)
    return completed.stdout.strip()


def init_repo(path: Path) -> Path:
    path.mkdir()
    git(path, "init", "-q")
    git(path, "config", "user.email", "audit@example.invalid")
    git(path, "config", "user.name", "Audit")
    return path


def commit_all(repo: Path, message: str) -> str:
    git(repo, "add", "-A")
    git(repo, "commit", "-qm", message)
    return git(repo, "rev-parse", "HEAD")


def copy_authorized_surface(destination: Path) -> None:
    for relative in MODULE.EXPECTED_MODIFIED + MODULE.EXPECTED_ADDITIVE:
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / relative, target)


def isolated_package_root(tmp_path: Path) -> Path:
    package = tmp_path / "package"
    package.mkdir()
    copy_authorized_surface(package)
    return package


def full_repository_with_committed_surface(tmp_path: Path) -> Path:
    repo = init_repo(tmp_path / "full-repository")
    (repo / "README.md").write_text("legitimate repository file\n")
    (repo / "docs").mkdir()
    (repo / "docs/UNRELATED_COMMITTED.txt").write_text("allowed outside package surface\n")
    copy_authorized_surface(repo)
    commit_all(repo, "full repository with exact authorized content")
    return repo


def repository_with_applied_surface(tmp_path: Path) -> Path:
    repo = init_repo(tmp_path / "application-repository")
    manifest = MODULE.load_manifest(ROOT)
    (repo / "README.md").write_text("legitimate repository file\n")
    for relative in MODULE.EXPECTED_MODIFIED + MODULE.EXPECTED_ADDITIVE:
        target = repo / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(MODULE.predecessor_package_bytes(manifest, ROOT, relative))
    commit_all(repo, "synthetic exact package v1.3 predecessor")
    for relative in MODULE.SUCCESSOR_CHANGED_PATHS:
        shutil.copy2(ROOT / relative, repo / relative)
    return repo


def make_layer_graph(tmp_path: Path) -> tuple[Path, str, str, str]:
    repo = init_repo(tmp_path / "repo")
    (repo / "x").write_text("base\n")
    predecessor = commit_all(repo, "predecessor")
    git(repo, "checkout", "-qb", "layer", predecessor)
    (repo / "x").write_text("layer\n")
    (repo / "y").write_text("additive\n")
    layer = commit_all(repo, "layer")
    git(repo, "checkout", "-qb", "base-side", predecessor)
    (repo / "z").write_text("base-side\n")
    commit_all(repo, "base-side")
    git(repo, "merge", "--no-ff", "layer", "-qm", "synthetic merge")
    merge = git(repo, "rev-parse", "HEAD")
    return repo, predecessor, layer, merge


def mini_manifest(predecessor: str) -> dict:
    return {
        "branch": "development",
        "modified_paths": ["x"],
        "additive_paths": ["y"],
        "predecessor": {"commit": predecessor},
        "pull_request": {
            "number": 34,
            "title": "WP6 successor-attestation layer",
            "base_branch": "main",
            "base_sha": MODULE.BASE_SHA,
            "head_branch": "development",
        },
        "successor_delta": {"modified_paths": ["x"], "additive_paths": ["y"]},
    }


def event_file(
    tmp_path: Path, head: str, valid: bool = True,
    *, number: int = 34, title: str = "WP6 successor-attestation layer",
    base_ref: str = "main", base_sha: str = MODULE.BASE_SHA,
    head_ref: str = "development",
) -> Path:
    path = tmp_path / "event.json"
    if valid:
        path.write_text(json.dumps({
            "number": number,
            "pull_request": {
                "title": title,
                "base": {"ref": base_ref, "sha": base_sha},
                "head": {"ref": head_ref, "sha": head},
            },
        }))
    else:
        path.write_text("{")
    return path


def test_isolated_exact_seventeen_file_package_archive_passes(tmp_path: Path) -> None:
    package = isolated_package_root(tmp_path)
    result = MODULE.validate_package_archive(package)
    assert result["status"] == "PASS"
    assert result["validation_context"] == MODULE.PACKAGE_ARCHIVE_CONTEXT


def test_full_repository_content_context_allows_unrelated_committed_files(tmp_path: Path) -> None:
    repo = full_repository_with_committed_surface(tmp_path)
    result = MODULE.validate_full_repository_content(repo)
    assert result["status"] == "PASS"
    assert result["validation_context"] == MODULE.FULL_REPOSITORY_CONTENT_CONTEXT


def test_compatibility_package_only_dispatch_uses_full_repository_context(tmp_path: Path) -> None:
    repo = full_repository_with_committed_surface(tmp_path)
    assert MODULE.validate_package(repo)["validation_context"] == MODULE.FULL_REPOSITORY_CONTENT_CONTEXT


def test_exact_four_modified_zero_additive_successor_application_surface_passes(tmp_path: Path) -> None:
    repo = repository_with_applied_surface(tmp_path)
    result = MODULE.validate_repository_application_surface(repo)
    assert result["validation_context"] == MODULE.REPOSITORY_APPLICATION_SURFACE_CONTEXT
    assert result["unstaged_modified_path_count"] == 4
    assert result["untracked_additive_path_count"] == 0


def test_manifest_and_exact_path_counts() -> None:
    manifest = MODULE.load_manifest(ROOT)
    assert manifest["modified_paths"] == MODULE.EXPECTED_MODIFIED
    assert manifest["additive_paths"] == MODULE.EXPECTED_ADDITIVE
    assert len(set(manifest["modified_paths"] + manifest["additive_paths"])) == 17


def test_four_root_classes_are_exact() -> None:
    assert MODULE.load_manifest(ROOT)["root_causes"] == MODULE.EXPECTED_ROOTS


def test_root_to_path_binding_is_complete() -> None:
    manifest = MODULE.load_manifest(ROOT)
    assert len(manifest["path_roles"]) == 17
    assert all(row["roots"] for row in manifest["path_roles"])
    for row in manifest["path_roles"]:
        if row["path"] in MODULE.EXPECTED_MODIFIED:
            assert row["roots"] == MODULE.EXPECTED_MODIFIED_ROOTS[row["path"]]
        else:
            assert row["roots"] == list(MODULE.EXPECTED_ROOTS)


def test_zero_unresolved_dependencies() -> None:
    assert MODULE.load_manifest(ROOT)["unresolved_dependency_count"] == 0


def test_prior_audit_findings_and_successor_resolutions_are_preserved_in_v14() -> None:
    manifest = MODULE.load_manifest(ROOT)
    assert manifest["version"] == "1.4"
    pre_resolution = manifest["pre_application_audit_resolution"]
    assert pre_resolution["predecessor_package_version"] == "1.0"
    assert pre_resolution["successor_package_version"] == "1.1"
    assert pre_resolution["status"] == "PASS"
    assert [row["defect_id"] for row in pre_resolution["corrected_findings"]] == [
        "PREAPP_DEFECT_1", "PREAPP_DEFECT_2"
    ]
    assert all(row["status"] == "RESOLVED" for row in pre_resolution["corrected_findings"])
    post_resolution = manifest["post_application_audit_resolution"]
    assert post_resolution["predecessor_package_version"] == "1.1"
    assert post_resolution["successor_package_version"] == "1.2"
    assert post_resolution["status"] == "PASS"
    assert [row["defect_id"] for row in post_resolution["corrected_findings"]] == [
        "POSTAPP_DEFECT_1"
    ]


    resolution = manifest["fixture_environment_propagation_resolution"]
    assert resolution["status"] == "RESOLVED"
    assert resolution["predecessor_package_version"] == "1.2"
    assert resolution["successor_package_version"] == "1.3"
    assert resolution["changed_internal_paths"] == MODULE.SUCCESSOR_CHANGED_PATHS
    test_resolution = manifest["pull_request_test_fixture_environment_isolation_resolution"]
    assert test_resolution == MODULE.expected_pull_request_test_fixture_resolution()
    assert test_resolution["predecessor_package_version"] == "1.3"
    assert test_resolution["successor_package_version"] == "1.4"


def test_self_excluding_ledger_has_sixteen_entries() -> None:
    rows = MODULE.parse_ledger((ROOT / MODULE.LEDGER).read_bytes())
    assert len(rows) == 16
    assert MODULE.LEDGER not in [path for _, path in rows]


def test_transformations_reproduce_all_modified_paths() -> None:
    manifest = MODULE.load_manifest(ROOT)
    assert [row["path"] for row in manifest["transformations"]] == MODULE.EXPECTED_MODIFIED
    for transformation in manifest["transformations"]:
        assert MODULE.apply_transform(transformation) == (ROOT / transformation["path"]).read_bytes()
        assert all(row["predecessor_anchor_count"] == 1 for row in transformation["replacements"])


def test_runtime_dependency_contract_is_exact() -> None:
    assert MODULE.load_manifest(ROOT)["runtime_dependencies"] == ["pytest", "jsonschema", "pyyaml"]


def test_all_modified_workflows_install_pyyaml_and_route_to_successor() -> None:
    for path in MODULE.EXPECTED_MODIFIED:
        text = (ROOT / path).read_text()
        assert "pytest jsonschema pyyaml" in text
        assert MODULE.VERIFIER in text


def test_dedicated_workflow_covers_all_seventeen_paths_twice() -> None:
    text = (ROOT / MODULE.WORKFLOW).read_text()
    for path in MODULE.EXPECTED_MODIFIED + MODULE.EXPECTED_ADDITIVE:
        assert text.count("      - '" + path + "'\n") == 2
    assert "--verify-all-replays" in text


def synthetic_fixture_contract(payloads: dict[str, bytes]) -> dict:
    return {
        "contract_id": "SYNTHETIC_FIXTURE",
        "source_commit": "a" * 40,
        "historical_replay_anchor": "b" * 40,
        "environment_variable": MODULE.FIXTURE_ENVIRONMENT_VARIABLE,
        "scope": "TEST_CHILD_PROCESSES_ONLY",
        "materialization": "SYNTHETIC_PROVIDER",
        "path_count": len(payloads),
        "files": [
            {"path": path, "git_blob_sha1": MODULE.git_blob_sha1(data)}
            for path, data in payloads.items()
        ],
        "historical_additive_paths_forbidden": MODULE.FOUR_ROOT_ADDITIVE_PATHS,
        "exact_inventory_required": True,
        "regular_files_only": True,
        "symlinks_forbidden": True,
        "extra_paths_forbidden": True,
        "cleanup_required": True,
        "source_repository_immutability_required": True,
        "unrelated_replay_environment_isolation_required": True,
    }


def synthetic_fixture_payloads() -> dict[str, bytes]:
    return {path: ("fixture:" + path + "\n").encode() for path in MODULE.FIXTURE_PATHS}


def test_successor_delta_is_exact_four_changed_thirteen_unchanged() -> None:
    manifest = MODULE.load_manifest(ROOT)
    assert manifest["successor_delta"] == MODULE.expected_successor_delta()
    identities = manifest["predecessor_package"]["file_identities"]
    changed = sorted(
        path for path in MODULE.EXPECTED_MODIFIED + MODULE.EXPECTED_ADDITIVE
        if MODULE.sha256_bytes((ROOT / path).read_bytes()) != identities[path]["sha256"]
    )
    assert changed == sorted(MODULE.SUCCESSOR_CHANGED_PATHS)


def test_manifest_fixture_contract_is_exact_and_scoped() -> None:
    manifest = MODULE.load_manifest(ROOT)
    assert manifest["fixture_contract"] == MODULE.expected_fixture_contract()
    assert manifest["replay_matrix"]["wp6-four-root"]["fixture_contract"] == MODULE.FIXTURE_CONTRACT_ID
    assert all(
        "fixture_contract" not in spec
        for name, spec in manifest["replay_matrix"].items()
        if name != "wp6-four-root"
    )


def test_fixture_materialization_positive(tmp_path: Path) -> None:
    payloads = synthetic_fixture_payloads()
    contract = synthetic_fixture_contract(payloads)
    fixture = tmp_path / "fixture"
    identities = MODULE.materialize_predecessor_fixture(fixture, contract, payloads.__getitem__)
    assert sorted(identities) == sorted(payloads)
    assert MODULE.validate_materialized_fixture(fixture, contract) == identities


def test_fixture_missing_path_is_rejected(tmp_path: Path) -> None:
    payloads = synthetic_fixture_payloads()
    contract = synthetic_fixture_contract(payloads)
    fixture = tmp_path / "fixture"
    MODULE.materialize_predecessor_fixture(fixture, contract, payloads.__getitem__)
    (fixture / MODULE.FIXTURE_PATHS[0]).unlink()
    with pytest.raises(RuntimeError, match="FIXTURE_EXACT_PATH_SET_FAILURE"):
        MODULE.validate_materialized_fixture(fixture, contract)


def test_fixture_wrong_identity_is_rejected(tmp_path: Path) -> None:
    payloads = synthetic_fixture_payloads()
    contract = synthetic_fixture_contract(payloads)
    fixture = tmp_path / "fixture"
    MODULE.materialize_predecessor_fixture(fixture, contract, payloads.__getitem__)
    (fixture / MODULE.FIXTURE_PATHS[0]).write_bytes(b"wrong\n")
    with pytest.raises(RuntimeError, match="FIXTURE_BLOB_IDENTITY_FAILURE"):
        MODULE.validate_materialized_fixture(fixture, contract)


def test_fixture_extra_path_is_rejected(tmp_path: Path) -> None:
    payloads = synthetic_fixture_payloads()
    contract = synthetic_fixture_contract(payloads)
    fixture = tmp_path / "fixture"
    MODULE.materialize_predecessor_fixture(fixture, contract, payloads.__getitem__)
    (fixture / "EXTRA.txt").write_text("extra\n")
    with pytest.raises(RuntimeError, match="FIXTURE_EXACT_PATH_SET_FAILURE"):
        MODULE.validate_materialized_fixture(fixture, contract)


def test_fixture_historical_additive_path_is_rejected(tmp_path: Path) -> None:
    payloads = synthetic_fixture_payloads()
    contract = synthetic_fixture_contract(payloads)
    fixture = tmp_path / "fixture"
    MODULE.materialize_predecessor_fixture(fixture, contract, payloads.__getitem__)
    additive = fixture / MODULE.FOUR_ROOT_ADDITIVE_PATHS[0]
    additive.parent.mkdir(parents=True, exist_ok=True)
    additive.write_text("forbidden\n")
    with pytest.raises(RuntimeError, match="FIXTURE_HISTORICAL_ADDITIVE_PATH_PRESENCE"):
        MODULE.validate_materialized_fixture(fixture, contract)


def test_fixture_cleanup_removes_temporary_tree(tmp_path: Path) -> None:
    payloads = synthetic_fixture_payloads()
    contract = synthetic_fixture_contract(payloads)
    manifest = {"fixture_contract": contract}
    parent = None
    with MODULE.predecessor_blob_fixture(tmp_path, manifest, payloads.__getitem__) as (fixture, identities):
        parent = fixture.parent
        assert fixture.is_dir()
        assert len(identities) == 3
    assert parent is not None and not parent.exists()


def test_replay_binds_fixture_environment_only_for_four_root(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    payloads = synthetic_fixture_payloads()
    contract = synthetic_fixture_contract(payloads)
    fixture = tmp_path / "fixture"
    MODULE.materialize_predecessor_fixture(fixture, contract, payloads.__getitem__)
    captured: list[dict[str, str]] = []
    manifest = {
        "fixture_contract": contract,
        "replay_matrix": {
            "wp6-four-root": {
                "anchor": "a" * 40,
                "commands": [["python", "child.py"]],
                "fixture_contract": MODULE.FIXTURE_CONTRACT_ID,
            }
        },
    }
    class Detached:
        def __enter__(self): return tmp_path
        def __exit__(self, *args): return False
    class Fixture:
        def __enter__(self): return fixture, {path: {} for path in payloads}
        def __exit__(self, *args): return False
    monkeypatch.setattr(MODULE, "verify_committed", lambda *args, **kwargs: {"status": "PASS"})
    monkeypatch.setattr(MODULE, "load_manifest", lambda repo: manifest)
    monkeypatch.setattr(MODULE, "repository_snapshot", lambda repo: {"stable": "yes"})
    monkeypatch.setattr(MODULE, "detached_worktree", lambda *args: Detached())
    monkeypatch.setattr(MODULE, "predecessor_blob_fixture", lambda *args, **kwargs: Fixture())
    monkeypatch.setattr(MODULE, "validate_exact_historical_context", lambda *args: None)
    monkeypatch.setattr(MODULE, "git_text", lambda *args, **kwargs: "")
    monkeypatch.setattr(
        MODULE, "require",
        lambda *args, cwd=None, env=None, text=True: captured.append(dict(env or {}))
        or subprocess.CompletedProcess(args, 0, "", ""),
    )
    result = MODULE.replay("wp6-four-root", repo=tmp_path)
    assert result["fixture_environment_bound"] == "YES"
    assert captured and captured[0][MODULE.FIXTURE_ENVIRONMENT_VARIABLE] == str(fixture)


def test_unrelated_replay_environment_isolation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    captured: list[dict[str, str]] = []
    manifest = {"replay_matrix": {"x": {"anchor": "a" * 40, "commands": [["python", "child.py"]]}}}
    class Detached:
        def __enter__(self): return tmp_path
        def __exit__(self, *args): return False
    monkeypatch.setenv(MODULE.FIXTURE_ENVIRONMENT_VARIABLE, "/contaminating/value")
    monkeypatch.setattr(MODULE, "verify_committed", lambda *args, **kwargs: {"status": "PASS"})
    monkeypatch.setattr(MODULE, "load_manifest", lambda repo: manifest)
    monkeypatch.setattr(MODULE, "repository_snapshot", lambda repo: {"stable": "yes"})
    monkeypatch.setattr(MODULE, "detached_worktree", lambda *args: Detached())
    monkeypatch.setattr(MODULE, "validate_exact_historical_context", lambda *args: None)
    monkeypatch.setattr(MODULE, "git_text", lambda *args, **kwargs: "")
    monkeypatch.setattr(
        MODULE, "require",
        lambda *args, cwd=None, env=None, text=True: captured.append(dict(env or {}))
        or subprocess.CompletedProcess(args, 0, "", ""),
    )
    result = MODULE.replay("x", repo=tmp_path)
    assert result["fixture_environment_bound"] == "NO"
    assert captured and MODULE.FIXTURE_ENVIRONMENT_VARIABLE not in captured[0]


def test_event_head_absent() -> None:
    assert MODULE.event_head(None) == ""


def test_event_head_invalid(tmp_path: Path) -> None:
    assert MODULE.event_head(str(event_file(tmp_path, "", valid=False))) == ""


def test_event_head_valid(tmp_path: Path) -> None:
    head = "a" * 40
    assert MODULE.event_head(str(event_file(tmp_path, head))) == head


def test_pull_request_event_requires_valid_head(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv("GITHUB_EVENT_PATH", raising=False)
    repo, predecessor, _, _ = make_layer_graph(tmp_path)
    with pytest.raises(RuntimeError, match="PULL_REQUEST_CONTEXT_MISSING_OR_INVALID"):
        MODULE.resolve_layer_head(repo, mini_manifest(predecessor), event_name="pull_request")


def test_invalid_event_payload_fails_closed(tmp_path: Path) -> None:
    repo, predecessor, _, _ = make_layer_graph(tmp_path)
    with pytest.raises(RuntimeError, match="PULL_REQUEST_CONTEXT_MISSING_OR_INVALID"):
        MODULE.resolve_layer_head(
            repo, mini_manifest(predecessor), str(event_file(tmp_path, "", valid=False)),
            event_name="pull_request",
        )


def test_valid_synthetic_merge_recovers_exact_pr_head(tmp_path: Path) -> None:
    repo, predecessor, layer, _ = make_layer_graph(tmp_path)
    event = event_file(tmp_path, layer)
    assert MODULE.resolve_layer_head(
        repo, mini_manifest(predecessor), str(event), event_name="pull_request"
    ) == layer


def test_synthetic_merge_is_not_unique_authority_but_parents_are_inspected(tmp_path: Path) -> None:
    repo, predecessor, layer, merge = make_layer_graph(tmp_path)
    assert git(repo, "rev-parse", "HEAD") == merge
    assert MODULE.resolve_layer_head(repo, mini_manifest(predecessor), event_name="push") == layer


def test_wrong_pull_request_head_is_rejected(tmp_path: Path) -> None:
    repo, predecessor, _, merge = make_layer_graph(tmp_path)
    event = event_file(tmp_path, merge)
    with pytest.raises(RuntimeError, match="PULL_REQUEST_HEAD_NOT_EXACT_LAYER"):
        MODULE.resolve_layer_head(
            repo, mini_manifest(predecessor), str(event), event_name="pull_request"
        )


def test_deep_ancestry_resolution_finds_exact_layer(tmp_path: Path) -> None:
    repo, predecessor, layer, _ = make_layer_graph(tmp_path)
    for ordinal in range(5):
        (repo / f"descendant-{ordinal}").write_text(str(ordinal))
        commit_all(repo, f"descendant-{ordinal}")
    assert MODULE.resolve_layer_head(repo, mini_manifest(predecessor), event_name="push") == layer


def test_zero_candidate_heads_fail_closed(tmp_path: Path) -> None:
    repo, predecessor, _, _ = make_layer_graph(tmp_path)
    manifest = mini_manifest("0" * 40)
    with pytest.raises(RuntimeError, match="LAYER_HEAD_RESOLUTION_FAILURE"):
        MODULE.resolve_layer_head(repo, manifest, event_name="push")


def test_incorrect_direct_parent_is_rejected(tmp_path: Path) -> None:
    repo = init_repo(tmp_path / "repo")
    (repo / "x").write_text("base\n")
    predecessor = commit_all(repo, "predecessor")
    (repo / "temporary").write_text("temporary\n")
    wrong_parent = commit_all(repo, "wrong-parent")
    (repo / "temporary").unlink()
    (repo / "x").write_text("layer\n")
    (repo / "y").write_text("additive\n")
    layer = commit_all(repo, "same-surface-wrong-parent")
    assert MODULE.diff_surface(repo, layer, predecessor) == {"x": "M", "y": "A"}
    assert git(repo, "rev-parse", layer + "^") == wrong_parent
    with pytest.raises(RuntimeError, match="LAYER_HEAD_RESOLUTION_FAILURE"):
        MODULE.resolve_layer_head(repo, mini_manifest(predecessor), event_name="push")


def test_multi_parent_layer_candidate_is_rejected(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo = init_repo(tmp_path / "repo")
    (repo / "x").write_text("base\n")
    predecessor = commit_all(repo, "predecessor")
    git(repo, "checkout", "-qb", "unreachable-layer", predecessor)
    (repo / "x").write_text("layer\n")
    (repo / "y").write_text("additive\n")
    unreachable_layer = commit_all(repo, "unreachable-layer")
    layer_tree = git(repo, "rev-parse", unreachable_layer + "^{tree}")
    git(repo, "checkout", "-qb", "side", predecessor)
    (repo / "z").write_text("side\n")
    side = commit_all(repo, "side")
    multi_parent = subprocess.run(
        ["git", "commit-tree", layer_tree, "-p", predecessor, "-p", side],
        cwd=repo, input="multi-parent-layer\n", capture_output=True, text=True, check=True,
    ).stdout.strip()
    git(repo, "reset", "--hard", "-q", multi_parent)
    git(repo, "branch", "-D", "unreachable-layer")
    assert MODULE.diff_surface(repo, multi_parent, predecessor) == {"x": "M", "y": "A"}
    assert len(git(repo, "rev-list", "--parents", "-n", "1", multi_parent).split()) == 3
    monkeypatch.delenv("V0_OSAP_EXACT_BRANCH_HEAD", raising=False)
    monkeypatch.delenv("GITHUB_SHA", raising=False)
    with pytest.raises(RuntimeError, match="LAYER_HEAD_RESOLUTION_FAILURE"):
        MODULE.resolve_layer_head(repo, mini_manifest(predecessor), event_name="push")


@pytest.mark.parametrize(
    ("field", "kwargs"),
    [
        ("number", {"number": 35}),
        ("title", {"title": "wrong title"}),
        ("base_ref", {"base_ref": "wrong-base"}),
        ("base_sha", {"base_sha": "0" * 40}),
        ("head_ref", {"head_ref": "wrong-head"}),
    ],
)
def test_wrong_live_pull_request_context_field_is_rejected(
    tmp_path: Path, field: str, kwargs: dict[str, object]
) -> None:
    repo, predecessor, layer, _ = make_layer_graph(tmp_path)
    event = event_file(tmp_path, layer, **kwargs)
    with pytest.raises(RuntimeError, match="PULL_REQUEST_CONTEXT_MISMATCH:" + field):
        MODULE.resolve_layer_head(
            repo, mini_manifest(predecessor), str(event), event_name="pull_request"
        )


def test_multiple_exact_layer_candidates_fail_closed(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    repo = init_repo(tmp_path / "repo")
    (repo / "x").write_text("base\n")
    predecessor = commit_all(repo, "predecessor")
    layers = []
    for name in ("layer-one", "layer-two"):
        git(repo, "checkout", "-qB", name, predecessor)
        (repo / "x").write_text("layer\n")
        (repo / "y").write_text("additive\n")
        layers.append(commit_all(repo, name))
    tree = git(repo, "rev-parse", layers[0] + "^{tree}")
    merge = subprocess.run(
        ["git", "commit-tree", tree, "-p", layers[0], "-p", layers[1]],
        cwd=repo, input="merge\n", capture_output=True, text=True, check=True,
    ).stdout.strip()
    git(repo, "reset", "--hard", "-q", merge)
    monkeypatch.delenv("V0_OSAP_EXACT_BRANCH_HEAD", raising=False)
    monkeypatch.delenv("GITHUB_SHA", raising=False)
    with pytest.raises(RuntimeError, match="LAYER_HEAD_RESOLUTION_FAILURE"):
        MODULE.resolve_layer_head(repo, mini_manifest(predecessor), event_name="push")


def test_wrong_predecessor_sha256_is_rejected() -> None:
    transformation = dict(MODULE.load_manifest(ROOT)["transformations"][0])
    transformation["predecessor_sha256"] = "0" * 64
    with pytest.raises(RuntimeError, match="PREDECESSOR_SHA256_FAILURE"):
        MODULE.apply_transform(transformation)


def test_wrong_predecessor_blob_is_rejected() -> None:
    transformation = dict(MODULE.load_manifest(ROOT)["transformations"][0])
    transformation["predecessor_blob_sha1"] = "0" * 40
    with pytest.raises(RuntimeError, match="PREDECESSOR_BLOB_FAILURE"):
        MODULE.apply_transform(transformation)


def test_missing_pyyaml_is_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    original = MODULE.importlib.util.find_spec
    monkeypatch.setattr(
        MODULE.importlib.util, "find_spec",
        lambda name: None if name == "yaml" else original(name),
    )
    with pytest.raises(RuntimeError, match="RUNTIME_DEPENDENCY_MISSING:yaml"):
        MODULE.ensure_runtime_dependencies()


def test_missing_historical_anchor_fails_closed(tmp_path: Path) -> None:
    repo = init_repo(tmp_path / "repo")
    (repo / "x").write_text("x\n")
    commit_all(repo, "base")
    manifest = {"replay_matrix": {"missing": {"anchor": "0" * 40, "commands": []}}}
    with pytest.raises(RuntimeError, match="MISSING_HISTORICAL_ANCHOR"):
        MODULE.validate_historical_anchors(repo, manifest)


def test_frozen_test_in_descendant_checkout_is_rejected(tmp_path: Path) -> None:
    repo = init_repo(tmp_path / "repo")
    (repo / "x").write_text("a\n")
    anchor = commit_all(repo, "anchor")
    (repo / "x").write_text("b\n")
    commit_all(repo, "descendant")
    with pytest.raises(RuntimeError, match="FROZEN_EXECUTION_CONTEXT_FAILURE"):
        MODULE.validate_exact_historical_context(repo, anchor)


def test_wp5_requires_exact_known_job() -> None:
    spec = MODULE.load_manifest(ROOT)["replay_matrix"]["wp5"]
    with pytest.raises(RuntimeError, match="INVALID_OR_MISSING_REPLAY_JOB"):
        MODULE.resolved_commands(spec, None)
    with pytest.raises(RuntimeError, match="INVALID_OR_MISSING_REPLAY_JOB"):
        MODULE.resolved_commands(spec, "unknown")
    command = MODULE.resolved_commands(spec, "baseline")[0]
    assert command[-2:] == ["--job", "baseline"]


def test_job_is_rejected_for_non_job_replay() -> None:
    spec = MODULE.load_manifest(ROOT)["replay_matrix"]["wp2"]
    with pytest.raises(RuntimeError, match="UNEXPECTED_REPLAY_JOB"):
        MODULE.resolved_commands(spec, "baseline")


def test_ledger_digest_mismatch_is_rejected(tmp_path: Path) -> None:
    package = isolated_package_root(tmp_path)
    target = package / MODULE.EXPECTED_MODIFIED[0]
    target.write_text(target.read_text() + "# mutation\n")
    with pytest.raises(RuntimeError, match="MODIFIED_BYTES_FAILURE|LEDGER_DIGEST_FAILURE"):
        MODULE.validate_package_archive(package)


def test_additive_predecessor_presence_is_rejected(tmp_path: Path) -> None:
    repo = init_repo(tmp_path / "repo")
    (repo / "new").write_text("already present\n")
    predecessor = commit_all(repo, "predecessor")
    with pytest.raises(RuntimeError, match="ADDITIVE_PREDECESSOR_PRESENCE:new"):
        MODULE.validate_additive_absence(repo, predecessor, ["new"])


def test_unrelated_eighteenth_file_is_rejected(tmp_path: Path) -> None:
    package = isolated_package_root(tmp_path)
    (package / "UNRELATED_EIGHTEENTH_PATH.txt").write_text("forbidden\n")
    with pytest.raises(RuntimeError, match="PACKAGE_EXACT_FILE_INVENTORY_FAILURE"):
        MODULE.validate_package_archive(package)


def test_missing_authorized_package_path_is_rejected(tmp_path: Path) -> None:
    package = isolated_package_root(tmp_path)
    (package / MODULE.EXPECTED_ADDITIVE[-1]).unlink()
    with pytest.raises(RuntimeError, match="PACKAGE_EXACT_FILE_INVENTORY_FAILURE"):
        MODULE.validate_package_archive(package)


@pytest.mark.parametrize("relative", MODULE.EXPECTED_MODIFIED + MODULE.EXPECTED_ADDITIVE)
def test_wrong_bytes_on_every_authorized_path_are_rejected(tmp_path: Path, relative: str) -> None:
    package = isolated_package_root(tmp_path)
    target = package / relative
    target.write_bytes(target.read_bytes() + b"# unauthorized mutation\n")
    with pytest.raises(RuntimeError):
        MODULE.validate_package_archive(package)


def test_unrelated_eighteenth_modified_worktree_path_is_rejected(tmp_path: Path) -> None:
    repo = repository_with_applied_surface(tmp_path)
    (repo / "README.md").write_text("unrelated mutation\n")
    with pytest.raises(RuntimeError, match="REPOSITORY_APPLICATION_SURFACE_FAILURE"):
        MODULE.validate_repository_application_surface(repo)


def test_unrelated_eighteenth_untracked_worktree_path_is_rejected(tmp_path: Path) -> None:
    repo = repository_with_applied_surface(tmp_path)
    (repo / "UNRELATED_UNTRACKED.txt").write_text("unrelated untracked\n")
    with pytest.raises(RuntimeError, match="REPOSITORY_APPLICATION_SURFACE_FAILURE"):
        MODULE.validate_repository_application_surface(repo)


def test_staged_path_is_rejected(tmp_path: Path) -> None:
    repo = repository_with_applied_surface(tmp_path)
    git(repo, "add", MODULE.SUCCESSOR_CHANGED_PATHS[0])
    with pytest.raises(RuntimeError, match="STAGED_PATH_PRESENT"):
        MODULE.validate_repository_application_surface(repo)


def test_full_repository_content_rejects_missing_authorized_path(tmp_path: Path) -> None:
    repo = full_repository_with_committed_surface(tmp_path)
    (repo / MODULE.EXPECTED_ADDITIVE[-1]).unlink()
    with pytest.raises(RuntimeError, match="AUTHORIZED_PATH_MISSING_OR_NONREGULAR"):
        MODULE.validate_full_repository_content(repo)


def test_verify_committed_uses_full_repository_content_not_archive_inventory(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    calls: list[Path] = []
    snapshot = {"state": "stable"}
    monkeypatch.setattr(MODULE, "repository_snapshot", lambda repo: snapshot)
    monkeypatch.setattr(MODULE, "load_manifest", lambda repo: {})
    monkeypatch.setattr(MODULE, "validate_manifest_contract", lambda manifest: None)
    monkeypatch.setattr(MODULE, "ensure_runtime_dependencies", lambda: None)
    monkeypatch.setattr(MODULE, "validate_predecessor_identity", lambda repo, manifest: None)
    monkeypatch.setattr(MODULE, "validate_historical_anchors", lambda repo, manifest: None)
    monkeypatch.setattr(MODULE, "resolve_layer_head", lambda *args, **kwargs: "a" * 40)
    monkeypatch.setattr(MODULE, "validate_committed_surface", lambda *args, **kwargs: None)
    monkeypatch.setattr(MODULE, "validate_full_repository_content", lambda repo: calls.append(repo))
    monkeypatch.setattr(
        MODULE, "validate_package",
        lambda repo: (_ for _ in ()).throw(AssertionError("archive validator must not run")),
    )
    result = MODULE.verify_committed(tmp_path)
    assert result["status"] == "PASS"
    assert calls == [tmp_path]


def test_repository_state_mutation_is_detected(monkeypatch: pytest.MonkeyPatch,
                                               tmp_path: Path) -> None:
    snapshots = iter([{"state": "before"}, {"state": "after"}])
    monkeypatch.setattr(MODULE, "verify_committed", lambda *args, **kwargs: {"status": "PASS"})
    monkeypatch.setattr(MODULE, "repository_snapshot", lambda repo: next(snapshots))
    monkeypatch.setattr(MODULE, "load_manifest", lambda repo: {
        "replay_matrix": {"x": {"anchor": "a", "commands": []}}
    })
    class Context:
        def __enter__(self):
            return tmp_path
        def __exit__(self, *args):
            return False
    monkeypatch.setattr(MODULE, "detached_worktree", lambda *args: Context())
    monkeypatch.setattr(MODULE, "validate_exact_historical_context", lambda *args: None)
    monkeypatch.setattr(MODULE, "git_text", lambda *args, **kwargs: "")
    with pytest.raises(RuntimeError, match="REPOSITORY_STATE_MUTATION"):
        MODULE.replay("x", repo=tmp_path)


def test_historical_artifacts_remain_frozen() -> None:
    policy = MODULE.load_manifest(ROOT)["historical_artifact_policy"]
    assert all(value is False for value in policy.values())


def test_context_matrix_is_complete() -> None:
    assert set(MODULE.load_manifest(ROOT)["pull_request_context_matrix"]) == MODULE.EXPECTED_CONTEXT_KEYS


def test_failure_policy_is_fail_closed() -> None:
    assert MODULE.load_manifest(ROOT)["behavioral_contract"]["failure_policy"] == "FAIL_CLOSED"


def test_package_contains_no_frozen_manifest_ledger_verifier_or_test_rewrites() -> None:
    paths = set(MODULE.EXPECTED_MODIFIED + MODULE.EXPECTED_ADDITIVE)
    forbidden_fragments = (
        "SUCCESSOR_ATTESTATION_LAYER_MANIFEST", "FOUR_ROOT_CORRECTIVE_LAYER_MANIFEST",
        "ROOT_D_SUCCESSOR_ATTESTED_OVERRIDE_MANIFEST", "HOSTED_CI_PREDECESSOR_BLOB_FIXTURE_CLOSURE_MANIFEST",
    )
    assert not any(any(fragment in path for fragment in forbidden_fragments) for path in paths)
