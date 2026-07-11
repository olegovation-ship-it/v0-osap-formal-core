from __future__ import annotations
from pathlib import Path
from v0_osap_fc1.fixtures import replay_fixture

ROOT = Path(__file__).resolve().parents[1]


def test_phase2_fixture_pairs_replay():
    names = [
        "positive/t127_closure_minimality", "negative/t127_nonminimal_closure",
        "positive/t128_alternative_support_transparency", "negative/t128_missing_support_selection",
        "positive/t129_compatibility_preservation", "negative/t129_incompatible_profile",
        "positive/t130_dimensional_readiness", "negative/t130_readiness_missing_prerequisite",
        "positive/t131_undefined_is_not_zero", "negative/t131_undefined_coerced_to_zero",
        "positive/t132_dle_history_adequacy", "negative/t132_dle_without_history",
    ]
    for name in names:
        result = replay_fixture(ROOT / f"fixtures/{name}.fixture.json")
        assert result["passed"], result
