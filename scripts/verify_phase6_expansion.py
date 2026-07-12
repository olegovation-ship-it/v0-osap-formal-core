from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

crosswalk = load("release/v1.3.0/theorem_crosswalk_phase6.json")
assert crosswalk["theorem_range"] == "T151-T156"
assert crosswalk["baseline_merge_commit"] == "8053709c73045f59358244ec58afc84cfd0deeb6"
assert crosswalk["normative_v1_1_reserved_range"] == "T121-T150"
assert crosswalk["extension_status"] == "POST_V1_1_EXPLICIT_DEVELOPMENT_EXTENSION"
assert crosswalk["phase5_status"] == "ACCEPTED_CI_PASS_MERGED_HISTORICALLY_PRESERVED"
assert crosswalk["phase6_status"] in {"BUILD_READY_CI_PENDING", "ACCEPTED_CI_PASS_MERGED"}

lean = (ROOT / "lean/V0OSAP/Phase6.lean").read_text(encoding="utf-8")
coq = (ROOT / "coq/theories/Phase6.v").read_text(encoding="utf-8")
phase6 = (ROOT / "checker/v0_osap_fc1/phase6.py").read_text(encoding="utf-8")
semantic = (ROOT / "checker/v0_osap_fc1/semantic.py").read_text(encoding="utf-8")

assert [row["theorem_id"] for row in crosswalk["records"]] == [
    f"T{i}" for i in range(151, 157)
]

for row in crosswalk["records"]:
    normalized = {
        key: row[key]
        for key in [
            "theorem_id", "canonical_name", "formal_signature",
            "assumptions", "conclusion",
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
    "EXTENSION_PROVENANCE_RECORD_REQUIRED",
    "UNDECLARED_EXTENSION_CLAIM_KIND",
    "DIAGNOSTIC_ENVELOPE_NONDETERMINISTIC",
    "EVIDENCE_PROVENANCE_CYCLE",
    "VERSION_LOCK_TUPLE_MISMATCH",
    "BASELINE_RESULT_CHANGED_BY_EXTENSION",
]:
    assert code in phase6

assert "phase6_diagnostics" in semantic

manifest = load("fixtures/manifest.json")
assert manifest["semantic_version"] == "FC-1-v1.1+phase6"
assert manifest["status"] == "PHASE6_T151_T156_EXTENSION_PATCH_ORACLE_SET"

required_fixtures = {
    "positive/t151_explicit_extension_provenance.fixture.json",
    "negative/t151_unrecorded_extension.fixture.json",
    "positive/t152_declared_claim_vocabulary_closure.fixture.json",
    "negative/t152_undeclared_claim_kind.fixture.json",
    "positive/t153_diagnostic_envelope_determinism.fixture.json",
    "negative/t153_diagnostic_envelope_mutation.fixture.json",
    "positive/t154_evidence_provenance_acyclicity.fixture.json",
    "negative/t154_evidence_provenance_cycle.fixture.json",
    "positive/t155_version_lock_coherence.fixture.json",
    "negative/t155_version_lock_mismatch.fixture.json",
    "positive/t156_conservative_extension_noninterference.fixture.json",
    "negative/t156_baseline_result_changed.fixture.json",
}
assert required_fixtures.issubset(set(manifest["fixtures"]))

workflow = (ROOT / ".github/workflows/release-readiness.yml").read_text(encoding="utf-8")
assert "python scripts/verify_phase6_expansion.py" in workflow

project = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
assert 'version = "0.7.0.dev1"' in project
assert '"implementation_version": "v0-osap-fc1/0.7.0.dev1"' in semantic

readme = (ROOT / "README.md").read_text(encoding="utf-8")
status = (ROOT / "docs/status_and_nonclaims.md").read_text(encoding="utf-8")
register = (ROOT / "docs/theorem_register.md").read_text(encoding="utf-8")
for text in (readme, status, register):
    assert "T151-T156" in text
    assert any(marker in text for marker in ("BUILD_READY", "BUILD READY", "ACCEPTED / CI PASS"))
    assert "8053709c73045f59358244ec58afc84cfd0deeb6" in text
    assert "10.5281/zenodo.21306969" in text

accepted_boundary = re.search(r"No accepted theorem IDs beyond T(\d+)", status)
assert accepted_boundary is not None
assert int(accepted_boundary.group(1)) >= 150

print("PASS: V0 OSAP v1.3.0 Phase 6 T151-T156 explicit extension cluster verified statically.")
