
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from rc1_audit_lib import apply_mutation, audit_inventory

ROOT = Path(__file__).resolve().parents[1]
RELEASE = ROOT / "release/v1.3.0"


def load(name: str) -> dict:
    return json.loads((RELEASE / name).read_text(encoding="utf-8"))


inventory = load("RC1_THEOREM_INVENTORY.json")
manifest = load("RC1_RELEASE_MANIFEST.json")
master_index = load("RC1_PROGRAM_MASTER_INDEX.json")
claim_matrix = load("RC1_CLAIM_CLASSIFICATION_MATRIX.json")
contract = load("RC1_VALIDATOR_EVIDENCE_INTERCHANGE_CONTRACT.json")
mutants = load("RC1_NEGATIVE_GATE_FIXTURES.json")
parity = load("RC1_STATEMENT_PARITY_EVIDENCE.json")

assert audit_inventory(inventory) == []
assert inventory["theorem_range"] == "T121-T156"
assert inventory["record_count"] == 36
assert parity["status"] == "PASS"
assert parity["record_count"] == 36
assert manifest["baseline_closure_commit"] == "29201b4937cef220ef0933d852250b021f3f44d4"
assert manifest["immutable_tag"] == "v1.2.0"
assert manifest["immutable_doi"] == "10.5281/zenodo.21306969"
assert all(value is False for value in manifest["release_actions"].values())
assert master_index["baseline_commit"] == "29201b4937cef220ef0933d852250b021f3f44d4"
assert "CONDITIONAL_THEOREM" in claim_matrix["classes"]
assert contract["outcomes"][-1] == "BACKEND_PARITY_FAILURE"

killed = []
for mutant in mutants["mutants"]:
    mutated = apply_mutation(inventory, mutant)
    diagnostics = audit_inventory(mutated)
    if mutant["expected"] not in diagnostics:
        raise AssertionError(
            f"Mutant {mutant['id']} survived: expected {mutant['expected']}, "
            f"got {diagnostics}"
        )
    killed.append({
        "id": mutant["id"],
        "expected": mutant["expected"],
        "diagnostics": diagnostics,
        "status": "KILLED",
    })

workflow = (ROOT / ".github/workflows/release-readiness.yml").read_text(encoding="utf-8")
for command in [
    "python scripts/build_rc1_release_inventory.py",
    "python scripts/verify_rc1_statement_parity.py",
    "python scripts/verify_rc1_gate_audit.py",
    "python scripts/verify_phase6_ci_closure.py",
    "python scripts/verify_manifest.py",
    "python scripts/verify_closure.py",
]:
    assert command in workflow

for required in [
    "README.md",
    "CHANGELOG.md",
    "docs/status_and_nonclaims.md",
    "release/v1.3.0/RC1_GATE_AUDIT_AND_RELEASE_FREEZE_SPECIFICATION.md",
    "release/v1.3.0/RC1_ACCEPTANCE_GATES.md",
]:
    assert (ROOT / required).exists(), required

readme = (ROOT / "README.md").read_text(encoding="utf-8")
status = (ROOT / "docs/status_and_nonclaims.md").read_text(encoding="utf-8")
for body in [readme, status]:
    assert (
        "RC1_AUDIT_READY" in body
        or "RC1_CLOSURE_READY" in body
    )
    assert (
        "NO RELEASE TAG" in body
        or "NO_RELEASE_TAG" in body
        or "TAG_NOT_CREATED" in body
    )
    assert "10.5281/zenodo.21306969" in body
    assert "T121-T156" in body

evidence = {
    "artifact_id": "V0_OSAP_V1_3_0_RC1_GATE_AUDIT_EVIDENCE",
    "version": "0.1",
    "date": "2026-07-13",
    "status": "RC1_AUDIT_READY_CI_PENDING",
    "theorem_range": "T121-T156",
    "baseline_closure_commit": "29201b4937cef220ef0933d852250b021f3f44d4",
    "structural_parity": "PASS",
    "negative_gate_mutants": {
        "total": len(killed),
        "killed": len(killed),
        "result": "PASS",
        "details": killed,
    },
    "historical_preservation": {
        "immutable_tag": "v1.2.0",
        "immutable_doi": "10.5281/zenodo.21306969",
        "release_created_by_patch": False,
    },
    "pending": [
        "complete GitHub Actions matrix",
        "merged-candidate audit",
        "independent clean-room replay",
        "separate RC1 closure decision",
    ],
    "claim_boundary": {
        "checker_completeness_claimed": False,
        "unconditional_global_soundness_claimed": False,
        "proof_term_identity_claimed": False,
        "global_conservativity_claimed": False,
        "empirical_or_physical_validation_claimed": False,
    },
}
evidence["evidence_sha256"] = hashlib.sha256(
    json.dumps(evidence, sort_keys=True, separators=(",", ":")).encode("utf-8")
).hexdigest()
(RELEASE / "RC1_GATE_AUDIT_EVIDENCE.json").write_text(
    json.dumps(evidence, indent=2, ensure_ascii=False) + "\n",
    encoding="utf-8",
)

print(
    "PASS: RC1 gate audit ready; 36 theorem records verified and "
    f"{len(killed)}/{len(killed)} negative gate mutants killed. "
    "No release tag created."
)
