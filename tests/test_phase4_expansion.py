
from __future__ import annotations

from pathlib import Path

from v0_osap_fc1.fixtures import replay_fixture

ROOT = Path(__file__).resolve().parents[1]

NAMES = [
    "positive/t139_archive_non_guard_export",
    "negative/t139_archive_guard_export",
    "positive/t140_independent_witness_certificate",
    "negative/t140_noncompliant_witness_certificate",
    "positive/t141_no_container",
    "negative/t141_v0_ordinary_contains_branch",
    "positive/t142_policy_based_branch_distinctness",
    "negative/t142_label_only_branch_distinctness",
    "positive/t143_countable_cardinality_licensed",
    "negative/t143_nonfinite_cardinality_unlicensed",
    "positive/t144_diagnostic_precedence_totality",
    "negative/t144_wrong_primary_status",
]


def test_phase4_fixture_pairs_replay():
    for name in NAMES:
        result = replay_fixture(ROOT / f"fixtures/{name}.fixture.json")
        assert result["passed"], result
