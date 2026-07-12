from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

crosswalk = load("release/v1.3.0/theorem_crosswalk_phase5.json")
assert crosswalk["theorem_range"] == "T145-T150"
assert crosswalk["baseline_merge_commit"] == "2a769d7723470cce59df81262b586abf19b9c750"
assert crosswalk["phase4_status"] == "ACCEPTED_CI_PASS_MERGED_HISTORICALLY_PRESERVED"
assert crosswalk["phase5_status"] in {"BUILD_READY_CI_PENDING", "ACCEPTED_CI_PASS_MERGED"}

lean = (ROOT / "lean/V0OSAP/Phase5.lean").read_text(encoding="utf-8")
coq = (ROOT / "coq/theories/Phase5.v").read_text(encoding="utf-8")
phase5 = (ROOT / "checker/v0_osap_fc1/phase5.py").read_text(encoding="utf-8")
canonical = (ROOT / "checker/v0_osap_fc1/canonical.py").read_text(encoding="utf-8")
semantic = (ROOT / "checker/v0_osap_fc1/semantic.py").read_text(encoding="utf-8")

assert [row["theorem_id"] for row in crosswalk["records"]] == [
    f"T{i}" for i in range(145, 151)
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
    "CANONICAL_SERIALIZATION_HASH_MISMATCH",
    "ROUND_TRIP_IDENTITY_MISMATCH",
    "REPLAY_NONDETERMINISTIC_RESULT",
    "HIDDEN_SCHEMA_MIGRATION_COERCION",
    "BACKEND_STATEMENT_HASH_MISMATCH",
    "CHECKER_PASS_VIOLATES_ACCEPTED_FRAGMENT_SOUNDNESS",
]:
    assert code in phase5

assert 'CANONICALIZATION_ID = "V0-OSAP-CJ-1"' in canonical
assert "phase5_diagnostics" in semantic

manifest = load("fixtures/manifest.json")
assert manifest["semantic_version"] == "FC-1-v1.1+phase5"
assert manifest["status"] == "PHASE5_T145_T150_PATCH_ORACLE_SET"

required_fixtures = {
    "positive/t145_canonical_serialization_determinism.fixture.json",
    "negative/t145_wrong_canonical_hash.fixture.json",
    "positive/t146_round_trip_identity.fixture.json",
    "negative/t146_round_trip_mutation.fixture.json",
    "positive/t147_replay_determinism.fixture.json",
    "negative/t147_nondeterministic_replay.fixture.json",
    "positive/t148_visible_schema_migration.fixture.json",
    "negative/t148_hidden_parser_coercion.fixture.json",
    "positive/t149_backend_statement_correspondence.fixture.json",
    "negative/t149_backend_statement_hash_mismatch.fixture.json",
    "positive/t150_accepted_fragment_checker_soundness.fixture.json",
    "negative/t150_checker_pass_unsound.fixture.json"
}
assert required_fixtures.issubset(set(manifest["fixtures"]))

workflow = (ROOT / ".github/workflows/release-readiness.yml").read_text(encoding="utf-8")
assert "python scripts/verify_phase5_expansion.py" in workflow
assert "python scripts/verify_manifest.py" in workflow
assert "python scripts/verify_closure.py" in workflow

project = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
assert 'version = "0.6.0.dev1"' in project
assert '"implementation_version": "v0-osap-fc1/0.6.0.dev1"' in semantic

readme = (ROOT / "README.md").read_text(encoding="utf-8")
status = (ROOT / "docs/status_and_nonclaims.md").read_text(encoding="utf-8")
register = (ROOT / "docs/theorem_register.md").read_text(encoding="utf-8")
for text in (readme, status, register):
    assert "T145-T150" in text
    assert any(marker in text for marker in ("BUILD_READY", "BUILD READY", "ACCEPTED / CI PASS"))
    assert "2a769d7723470cce59df81262b586abf19b9c750" in text
    assert "10.5281/zenodo.21306969" in text

accepted_boundary = re.search(r"No accepted theorem IDs beyond T(\d+)", status)
assert accepted_boundary is not None
assert int(accepted_boundary.group(1)) >= 144
print("PASS: V0 OSAP v1.3.0 Phase 5 T145-T150 theorem cluster verified statically.")
