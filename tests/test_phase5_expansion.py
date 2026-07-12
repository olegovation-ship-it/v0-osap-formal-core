from __future__ import annotations

from pathlib import Path

from v0_osap_fc1.fixtures import replay_fixture

ROOT = Path(__file__).resolve().parents[1]

NAMES = [
    "positive/t145_canonical_serialization_determinism",
    "negative/t145_wrong_canonical_hash",
    "positive/t146_round_trip_identity",
    "negative/t146_round_trip_mutation",
    "positive/t147_replay_determinism",
    "negative/t147_nondeterministic_replay",
    "positive/t148_visible_schema_migration",
    "negative/t148_hidden_parser_coercion",
    "positive/t149_backend_statement_correspondence",
    "negative/t149_backend_statement_hash_mismatch",
    "positive/t150_accepted_fragment_checker_soundness",
    "negative/t150_checker_pass_unsound",
]

def test_phase5_fixture_pairs_replay():
    for name in NAMES:
        result = replay_fixture(ROOT / f"fixtures/{name}.fixture.json")
        assert result["passed"], result
