from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


crosswalk = load("release/v1.3.0/theorem_crosswalk_phase4.json")
assert crosswalk["theorem_range"] == "T139-T144"
assert crosswalk["baseline_merge_commit"] == "24fc12fa0fce3d2b67ebe684e00ef7bb8537cf30"
assert crosswalk["phase3_status"] == "ACCEPTED_CI_PASS_MERGED_HISTORICALLY_PRESERVED"
assert crosswalk["phase4_status"] in {"BUILD_READY_CI_PENDING", "ACCEPTED_CI_PASS_MERGED"}

lean = (ROOT / "lean/V0OSAP/Phase4.lean").read_text(encoding="utf-8")
coq = (ROOT / "coq/theories/Phase4.v").read_text(encoding="utf-8")
semantic = (ROOT / "checker/v0_osap_fc1/semantic.py").read_text(encoding="utf-8")

assert [row["theorem_id"] for row in crosswalk["records"]] == [
    f"T{i}" for i in range(139, 145)
]

for row in crosswalk["records"]:
    normalized = {
        key: row[key]
        for key in [
            "theorem_id",
            "canonical_name",
            "formal_signature",
            "assumptions",
            "conclusion",
        ]
    }
    expected = hashlib.sha256(
        json.dumps(normalized, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    assert row["canonical_statement_sha256"] == expected
    assert row["lean_symbol"].split(".")[-1] in lean
    assert row["coq_symbol"] in coq
    assert row["parity_status"] in {"PATCH_READY_CI_PENDING", "ACCEPTED_CI_PASS"}

for code in [
    "ARCHIVE_CANNOT_EXPORT_CURRENT_GUARD",
    "INDEPENDENT_WITNESS_CERTIFICATE_UNSUPPORTED",
    "V0_ORDINARY_CONTAINS_FORBIDDEN",
    "BRANCH_LABELS_DO_NOT_PROVE_DISTINCTNESS",
    "DEFERRED_CARDINALITY_CERT",
    "DIAGNOSTIC_PRIMARY_STATUS_MISMATCH",
]:
    assert code in semantic

manifest = load("fixtures/manifest.json")
assert manifest["semantic_version"] == "FC-1-v1.1+phase4"
assert manifest["status"] == "PHASE4_T139_T144_PATCH_ORACLE_SET"

required_fixtures = {
    "positive/t139_archive_non_guard_export.fixture.json",
    "negative/t139_archive_guard_export.fixture.json",
    "positive/t140_independent_witness_certificate.fixture.json",
    "negative/t140_noncompliant_witness_certificate.fixture.json",
    "positive/t141_no_container.fixture.json",
    "negative/t141_v0_ordinary_contains_branch.fixture.json",
    "positive/t142_policy_based_branch_distinctness.fixture.json",
    "negative/t142_label_only_branch_distinctness.fixture.json",
    "positive/t143_countable_cardinality_licensed.fixture.json",
    "negative/t143_nonfinite_cardinality_unlicensed.fixture.json",
    "positive/t144_diagnostic_precedence_totality.fixture.json",
    "negative/t144_wrong_primary_status.fixture.json",
}
assert required_fixtures.issubset(set(manifest["fixtures"]))

workflow = (ROOT / ".github/workflows/release-readiness.yml").read_text(encoding="utf-8")
for command in [
    "python scripts/verify_phase1_alignment.py",
    "python scripts/verify_phase2_expansion.py",
    "python scripts/verify_phase2_ci_closure.py",
    "python scripts/verify_phase3_expansion.py",
    "python scripts/verify_phase3_ci_closure.py",
    "python scripts/verify_phase4_expansion.py",
    "python scripts/verify_phase4_ci_closure.py",
    "python scripts/verify_manifest.py",
    "python scripts/verify_closure.py",
]:
    assert command in workflow

project = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
assert 'version = "0.5.0.dev1"' in project
assert '"implementation_version": "v0-osap-fc1/0.5.0.dev1"' in semantic

readme = (ROOT / "README.md").read_text(encoding="utf-8")
status = (ROOT / "docs/status_and_nonclaims.md").read_text(encoding="utf-8")
register = (ROOT / "docs/theorem_register.md").read_text(encoding="utf-8")
for text in (readme, status, register):
    assert "T139-T144" in text
    assert any(marker in text for marker in ("BUILD_READY", "BUILD READY", "ACCEPTED / CI PASS"))
assert "24fc12fa0fce3d2b67ebe684e00ef7bb8537cf30" in readme
assert "10.5281/zenodo.21306969" in status
assert any(marker in status for marker in ("No accepted theorem IDs beyond T138", "No accepted theorem IDs beyond T144"))

print("PASS: V0 OSAP v1.3.0 Phase 4 T139-T144 theorem cluster verified statically.")
