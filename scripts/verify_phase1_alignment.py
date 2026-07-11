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
assert '"implementation_version": "v0-osap-fc1/0.2.0.dev1"' in semantic

lean = (ROOT / "lean/V0OSAP/Observer.lean").read_text(encoding="utf-8")
coq = (ROOT / "coq/theories/Observer.v").read_text(encoding="utf-8")
for text in (lean, coq):
    assert "terminal_self_certificate" in text.lower() or "TerminalSelfCertificate" in text
    assert "admissible" in text.lower()

crosswalk = load("release/v1.3.0/theorem_crosswalk_phase1.json")
records = {item["theorem_id"]: item for item in crosswalk["records"]}
assert set(records) == {"T121", "T122", "T123", "T124", "T125", "T126"}
for target in ("T122", "T124", "T125"):
    assert records[target]["phase1_blocker_status"] == "CLOSED_BY_PATCH_PENDING_CI"

print("PASS: V0 OSAP v1.3.0 Phase 1 semantic-alignment patch verified statically.")
