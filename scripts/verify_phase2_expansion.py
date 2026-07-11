from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


crosswalk = load("release/v1.3.0/theorem_crosswalk_phase2.json")
assert crosswalk["theorem_range"] == "T127-T132"
assert crosswalk["phase1_status"] == "ACCEPTED_CI_PASS"
assert crosswalk["phase2_status"] == "ACCEPTED_CI_PASS_MERGED"

lean = (ROOT / "lean/V0OSAP/Expansion.lean").read_text(encoding="utf-8")
coq = (ROOT / "coq/theories/Expansion.v").read_text(encoding="utf-8")
semantic = (ROOT / "checker/v0_osap_fc1/semantic.py").read_text(encoding="utf-8")

assert [row["theorem_id"] for row in crosswalk["records"]] == [
    f"T{i}" for i in range(127, 133)
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
    assert row["parity_status"] == "ACCEPTED_CI_PASS"

for code in [
    "PREREQUISITE_CLOSURE_NOT_LEAST",
    "ALTERNATIVE_SUPPORT_SELECTION_REQUIRED",
    "INVALID_ALTERNATIVE_SUPPORT_SELECTION",
    "COMPATIBILITY_CONSTRAINT_VIOLATION",
    "PROTOCOL_READY_WITHOUT_LIVE_PREREQUISITES",
    "UNDEFINED_DOMAIN_COERCED_TO_NUMERIC",
]:
    assert code in semantic

manifest = load("fixtures/manifest.json")
assert manifest["semantic_version"] in {"FC-1-v1.1+phase2", "FC-1-v1.1+phase3"}

workflow = (ROOT / ".github/workflows/release-readiness.yml").read_text(
    encoding="utf-8"
)
for command in [
    "python scripts/verify_phase1_alignment.py",
    "python scripts/verify_phase2_expansion.py",
    "python scripts/verify_phase2_ci_closure.py",
    "python scripts/verify_manifest.py",
    "python scripts/verify_closure.py",
]:
    assert command in workflow

project = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
assert any(version in project for version in ('version = "0.3.0.dev1"', 'version = "0.4.0.dev1"'))
assert any(version in semantic for version in (
    '"implementation_version": "v0-osap-fc1/0.3.0.dev1"',
    '"implementation_version": "v0-osap-fc1/0.4.0.dev1"',
))

print("PASS: V0 OSAP v1.3.0 Phase 2 T127-T132 accepted expansion verified statically.")
