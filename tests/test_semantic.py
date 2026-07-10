import json

from v0_osap_fc1.paths import fixture_root
from v0_osap_fc1.semantic import check_registry


def load(name: str):
    with (fixture_root() / name).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def test_positive_live_guard_passes():
    assert check_registry(load("positive/live_guard.registry.json"))["status"] == "PASS"


def test_unguarded_value_rejected():
    result = check_registry(load("negative/unguarded_value.registry.json"))
    assert result["status"] == "REJECT"
    assert [d["code"] for d in result["diagnostics"]] == ["UNGUARDED_VALUE_CLAIM"]
