from __future__ import annotations
from pathlib import Path
from v0_osap_fc1.fixtures import replay_fixture

ROOT = Path(__file__).resolve().parents[1]

NAMES = [
    "positive/t133_fresh_token_reactivation", "negative/t133_reused_token_identifier",
    "positive/t134_raw_relative_v0_no_live_residual", "negative/t134_live_residual_obstruction",
    "positive/t135_robust_relative_v0_no_live_noneliminable_residual", "negative/t135_live_noneliminable_residual_obstruction",
    "positive/t136_absolute_v0_independent_basis", "negative/t136_relative_to_absolute_promotion",
    "positive/t137_v0_identity_independent_basis", "negative/t137_approximation_identity_promotion",
    "positive/t138_cross_state_terminal_certificate", "negative/t138_same_state_self_certification",
]


def test_phase3_fixture_pairs_replay():
    for name in NAMES:
        result = replay_fixture(ROOT / f"fixtures/{name}.fixture.json")
        assert result["passed"], result
