from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = "7b38ddd6cb9bcfdc7c5713ba73a2c45d6513fbb8"


def test_rc1_inventory_builder_is_historical_replay() -> None:
    text = (ROOT / "scripts/build_rc1_release_inventory.py").read_text(
        encoding="utf-8"
    )
    assert SNAPSHOT in text
    assert "historical_blob" in text
    assert "FROZEN_OUTPUTS" in text
    assert "write_bytes" in text


def test_rc1_gate_audit_checkout_has_full_history() -> None:
    text = (ROOT / ".github/workflows/rc1-gate-audit.yml").read_text(
        encoding="utf-8"
    )
    assert "fetch-depth: 0" in text
