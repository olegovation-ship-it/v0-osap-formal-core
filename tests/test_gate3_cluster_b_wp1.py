from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(rel: str):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def load_module(name: str, rel: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_wp1_schemas_and_records_validate():
    module = load_module("wp1_verify", "scripts/verify_gate3_cluster_b_wp1.py")
    assert module.validate_records(ROOT) == []
    assert module.ledger_errors(ROOT) == []


def test_theorem_id_and_statement_closure():
    registry = load("release/v1.4.0/GATE3_CLUSTER_B_WP1_THEOREM_REGISTRY_T157_T162.json")
    assert registry["record_count"] == 6
    assert {r["theorem_id"] for r in registry["records"]} == {"T157","T158","T159","T160","T161","T162"}
    assert {r["theorem_id"] for r in registry["records"] if r["conditional"]} == {"T158","T160"}
    assert all(r["proof_status"] == "DEFERRED_TO_WP4_NOT_CLAIMED" for r in registry["records"])


def test_role_coverage_is_seven_of_seven():
    roles = load("release/v1.4.0/GATE3_CLUSTER_B_WP1_SEMANTIC_ROLE_MAP.json")
    assert roles["required_role_count"] == len(roles["roles"]) == 7
    assert roles["owner_assignment_complete"] is True
    assert all(r["registry_coverage"].startswith("COMPLETE") for r in roles["roles"])


def test_contract_owners_cover_new_theorems():
    contracts = load("release/v1.4.0/GATE3_CLUSTER_B_WP1_CANONICAL_CONTRACTS.json")
    assert {c["owner_theorem_id"] for c in contracts["contracts"]} == {"T157","T158","T159","T160","T161","T162"}


def test_dependency_dag_is_acyclic_and_declared():
    module = load_module("wp1_verify_dag", "scripts/verify_gate3_cluster_b_wp1.py")
    dag = load("release/v1.4.0/GATE3_CLUSTER_B_WP1_DEPENDENCY_DAG.json")
    assert module.dag_errors(dag) == []
    assert {x["theorem_id"] for x in dag["external_dependencies"]} == {"T131","T133"}
    t158 = next(n for n in dag["nodes"] if n["theorem_id"] == "T158")
    assert "T162" in t158["requires"]


def test_collision_audit_is_live_and_clean():
    module = load_module("wp1_verify_collision", "scripts/verify_gate3_cluster_b_wp1.py")
    record = load("release/v1.4.0/GATE3_CLUSTER_B_WP1_THEOREM_ID_COLLISION_AUDIT.json")
    assert module.collision_scan(ROOT) == []
    assert record["collisions"] == []
    assert record["audit_status"] == "PASS"


def test_release_and_proof_firewalls():
    lock = load("release/v1.4.0/GATE3_CLUSTER_B_WP1_BASELINE_LOCK.json")
    gates = load("release/v1.4.0/GATE3_CLUSTER_B_WP1_ACCEPTANCE_GATES.json")
    assert lock["wp1_authorization"]["release_actions_authorized"] is False
    assert lock["wp1_authorization"]["proof_implementation_authorized"] is False
    assert lock["wp1_authorization"]["closed_wp0_record_mutation_authorized"] is False
    assert gates["release_actions_authorized"] is False


def test_allowlist_patch_transform_is_idempotent_and_compilable():
    module = load_module("wp1_allowlist_patch", "release/v1.4.0/tools/patch_wp0_wp1_allowlist.py")
    sample = 'ALLOWED_FILES = {\n    "existing",\n}\n\nALLOWED_DIRECTORIES = (\n)\n'
    patched = module.patch_verifier_text(sample)
    assert all(f'    "{p}",' in patched for p in module.NEW_ALLOWED)
    assert module.patch_verifier_text(patched) == patched
    ast.parse(patched)

    test_sample = "from __future__ import annotations\nimport importlib.util\nfrom pathlib import Path\nROOT = Path('.')\n"
    test_patched = module.patch_test_text(test_sample)
    assert module.TEST_MARKER in test_patched
    assert module.patch_test_text(test_patched) == test_patched
    ast.parse(test_patched)
    assert "\\n" not in test_patched
    assert "\\\"" not in test_patched


def test_builder_outputs_are_current():
    module = load_module("wp1_builder", "scripts/build_gate3_cluster_b_wp1.py")
    overrides, ledger = module.expected_outputs()
    assert all(path.read_text(encoding="utf-8") == expected for path, expected in overrides.items())
    assert (ROOT / "release/v1.4.0/GATE3_CLUSTER_B_WP1_SHA256SUMS.txt").read_text(encoding="utf-8") == ledger


def test_git_commit_object_expression_is_literal_and_validly_escaped():
    module = load_module("wp1_verify_git_expr", "scripts/verify_gate3_cluster_b_wp1.py")
    assert module.BASE_COMMIT_OBJECT == module.BASE + "^{commit}"


def test_collision_scan_detects_suffixed_lean_and_coq_declarations(tmp_path):
    module = load_module("wp1_verify_formal_collision", "scripts/verify_gate3_cluster_b_wp1.py")
    lean = tmp_path / "lean" / "Collision.lean"
    coq = tmp_path / "coq" / "Collision.v"
    lean.parent.mkdir(parents=True)
    coq.parent.mkdir(parents=True)
    lean.write_text("theorem T157_strong_dle_certification : True := by trivial\n", encoding="utf-8")
    coq.write_text("Theorem T160_model_pair_noneliminability : True. Proof. exact I. Qed.\n", encoding="utf-8")
    collisions = module.collision_scan(tmp_path)
    assert any("formal declaration T157" in item for item in collisions)
    assert any("formal declaration T160" in item for item in collisions)


def test_collision_scan_ignores_non_string_schema_theorem_ids(tmp_path):
    module = load_module(
        "wp1_verify_schema_collision",
        "scripts/verify_gate3_cluster_b_wp1.py",
    )
    schema = tmp_path / "schemas" / "legacy_theorem.schema.json"
    schema.parent.mkdir(parents=True)
    schema.write_text(
        json.dumps({
            "properties": {
                "theorem_id": {"type": "string"}
            }
        }),
        encoding="utf-8",
    )
    assert module.collision_scan(tmp_path) == []


def test_wp0_post_merge_sha256_supersession_is_exact():
    def read_ledger(rel: str) -> dict[str, str]:
        entries: dict[str, str] = {}
        for line in (ROOT / rel).read_text(
            encoding="utf-8"
        ).splitlines():
            if not line.strip():
                continue
            expected, path = line.split("  ", 1)
            entries[path] = expected
        return entries

    historical = read_ledger(
        "release/v1.4.0/"
        "GATE3_CLUSTER_B_WP0_POST_MERGE_SHA256SUMS.txt"
    )
    successor = read_ledger(
        "release/v1.4.0/"
        "GATE3_CLUSTER_B_WP1_SHA256SUMS.txt"
    )

    superseded = {
        "scripts/verify_gate3_cluster_b_wp0.py",
        "scripts/verify_gate3_cluster_b_wp0_post_merge_closeout.py",
        "tests/test_gate3_cluster_b_wp0.py",
        "tests/test_gate3_cluster_b_wp0_post_merge_closeout.py",
    }

    assert set(historical) & set(successor) == superseded

    for rel in superseded:
        observed = hashlib.sha256(
            (ROOT / rel).read_bytes()
        ).hexdigest()

        assert observed == successor[rel]
        assert successor[rel] != historical[rel]
