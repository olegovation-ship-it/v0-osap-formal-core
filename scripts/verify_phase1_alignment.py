from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]


def load(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


schema = load("schemas/v1.1/registry_state.schema.json")
Draft202012Validator.check_schema(schema)

# T122 schema contract.
family_schema = schema["properties"]["prerequisite_families"]["items"]
assert "minItems" not in family_schema["properties"]["prerequisite_register_ids"]
assert family_schema["allOf"][0]["then"]["properties"]["prerequisite_register_ids"]["minItems"] == 1

fixture_manifest = load("fixtures/manifest.json")
required_paths = {
    "positive/empty_all_prerequisites.fixture.json",
    "positive/robust_relative_v0_no_live_residual.fixture.json",
    "negative/live_residual_obstruction.fixture.json",
    "positive/terminal_self_certificate_exhausted.fixture.json",
    "negative/terminal_self_certificate_not_exhausted.fixture.json",
}
assert required_paths.issubset(set(fixture_manifest["fixtures"]))

for rel in required_paths:
    descriptor = load("fixtures/" + rel)
    for target in descriptor["theorem_targets"]:
        assert target in {"T122", "T124", "T125"}

legacy = load("fixtures/negative/observer_self_certificate.fixture.json")
assert legacy["theorem_targets"] == []
assert legacy["expected_diagnostics"] == ["OBSERVER_CERTIFICATION_SUPPORT_REQUIRED"]

missing = load("fixtures/negative/missing_prerequisite.fixture.json")
assert missing["theorem_targets"] == []

semantic = (ROOT / "checker/v0_osap_fc1/semantic.py").read_text(encoding="utf-8")
for code in (
    "LIVE_RESIDUAL_OBSTRUCTS_ROBUST_RELATIVE_V0",
    "TERMINAL_SELF_CERTIFICATE_NOT_EXHAUSTED",
    "OBSERVER_CERTIFICATION_SUPPORT_REQUIRED",
):
    assert code in semantic
assert any(version in semantic for version in (
    '"implementation_version": "v0-osap-fc1/0.2.0.dev1"',
    '"implementation_version": "v0-osap-fc1/0.3.0.dev1"',
    '"implementation_version": "v0-osap-fc1/0.4.0.dev1"',
))

lean = (ROOT / "lean/V0OSAP/Observer.lean").read_text(encoding="utf-8")
coq = (ROOT / "coq/theories/Observer.v").read_text(encoding="utf-8")
for text in (lean, coq):
    assert "terminal_self_certificate" in text.lower() or "TerminalSelfCertificate" in text
    assert "admissible" in text.lower()

crosswalk = load("release/v1.3.0/theorem_crosswalk_phase1.json")
records = {item["theorem_id"]: item for item in crosswalk["records"]}
assert set(records) == {"T121", "T122", "T123", "T124", "T125", "T126"}
assert crosswalk["status"] == "PHASE1_ACCEPTED_CI_PASS"
for target in ("T122", "T124", "T125"):
    assert records[target]["phase1_blocker_status"] == "CLOSED_ACCEPTED_CI_PASS"

schema_manifest = load("release/v1.3.0/schema_erratum_manifest.json")
assert schema_manifest["status"] == "ERRATUM_ACCEPTED_CI_PASS"

workflow = (ROOT / ".github/workflows/release-readiness.yml").read_text(encoding="utf-8")
assert "ref: v1.2.0" in workflow
assert "python scripts/verify_manifest.py" in workflow
assert "python scripts/verify_closure.py" in workflow
assert "python scripts/verify_phase1_alignment.py" in workflow

closure_docs = [
    "release/v1.3.0/PHASE1_ACCEPTANCE_GATES.md",
    "release/v1.3.0/PHASE1_SEMANTIC_ALIGNMENT_REPORT.md",
    "release/v1.3.0/PHASE1_CI_CLOSURE_AND_HISTORICAL_PRESERVATION_REPORT.md",
]
for path in closure_docs:
    text = (ROOT / path).read_text(encoding="utf-8")
    assert "CI_PENDING" not in text
    assert "CLOSED_BY_PATCH_PENDING_CI" not in text

changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
assert "## [1.2.0] - 2026-07-11" in changelog
assert "48db564c085aec411552e78eef6c1740bd27a5ac" in changelog
assert "10.5281/zenodo.21306969" in changelog
assert "Closure verification script and final release-readiness gate." in changelog

print("PASS: V0 OSAP v1.3.0 Phase 1 accepted, CI-closed, and historically preserved.")
