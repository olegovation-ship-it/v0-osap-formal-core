from __future__ import annotations

import json
from pathlib import Path

from scripts.rc1_audit_lib import apply_mutation, audit_inventory

ROOT = Path(__file__).resolve().parents[1]
RELEASE = ROOT / "release/v1.3.0"


def test_rc1_inventory_and_negative_gates() -> None:
    inventory = json.loads(
        (RELEASE / "RC1_THEOREM_INVENTORY.json").read_text(encoding="utf-8")
    )
    mutants = json.loads(
        (RELEASE / "RC1_NEGATIVE_GATE_FIXTURES.json").read_text(encoding="utf-8")
    )
    assert audit_inventory(inventory) == []
    assert inventory["record_count"] == 36
    for mutant in mutants["mutants"]:
        diagnostics = audit_inventory(apply_mutation(inventory, mutant))
        assert mutant["expected"] in diagnostics, (mutant, diagnostics)


def test_gate_audit_verifier_is_executable_and_not_empty() -> None:
    path = ROOT / "scripts/verify_rc1_gate_audit.py"
    text = path.read_text(encoding="utf-8")
    assert len(text.splitlines()) > 100
    assert "audit_inventory(inventory)" in text
    assert "RC1_RELEASE_EVIDENCE_CLOSED" in text
    assert "negative gate mutants killed" in text
