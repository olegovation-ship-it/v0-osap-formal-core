from __future__ import annotations

import json
from pathlib import Path

from checker.v0_osap_fc1.semantic import check_registry

ROOT = Path(__file__).resolve().parents[1]

def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))

def test_phase6_fixture_pairs_replay() -> None:
    names = [
        "t151_explicit_extension_provenance",
        "t151_unrecorded_extension",
        "t152_declared_claim_vocabulary_closure",
        "t152_undeclared_claim_kind",
        "t153_diagnostic_envelope_determinism",
        "t153_diagnostic_envelope_mutation",
        "t154_evidence_provenance_acyclicity",
        "t154_evidence_provenance_cycle",
        "t155_version_lock_coherence",
        "t155_version_lock_mismatch",
        "t156_conservative_extension_noninterference",
        "t156_baseline_result_changed",
    ]
    for name in names:
        polarity = "positive" if name in {
            "t151_explicit_extension_provenance",
            "t152_declared_claim_vocabulary_closure",
            "t153_diagnostic_envelope_determinism",
            "t154_evidence_provenance_acyclicity",
            "t155_version_lock_coherence",
            "t156_conservative_extension_noninterference",
        } else "negative"
        descriptor = load(ROOT / "fixtures" / polarity / f"{name}.fixture.json")
        registry = load(ROOT / "fixtures" / polarity / descriptor["input_file"])
        result = check_registry(registry)
        assert result["status"] == descriptor["expected_status"], (name, result)
        assert [item["code"] for item in result["diagnostics"]] == descriptor["expected_diagnostics"], (name, result)
