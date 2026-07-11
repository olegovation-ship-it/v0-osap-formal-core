import json

from v0_osap_fc1.paths import fixture_root
from v0_osap_fc1.schema_validation import validate_instance
from v0_osap_fc1.semantic import check_registry


def load(name: str):
    with (fixture_root() / name).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def codes(result):
    return [item["code"] for item in result["diagnostics"]]


def test_t122_empty_all_of_is_schema_valid_and_passes():
    registry = load("positive/empty_all_prerequisites.registry.json")
    assert validate_instance(registry, "registry_state.schema.json") == []
    assert check_registry(registry)["status"] == "PASS"


def test_t124_live_residual_obstructs_robust_relative_v0():
    result = check_registry(load("negative/live_residual_obstruction.registry.json"))
    assert result["status"] == "REJECT"
    assert codes(result) == ["LIVE_RESIDUAL_OBSTRUCTS_ROBUST_RELATIVE_V0"]


def test_t124_no_live_residual_passes():
    assert check_registry(load("positive/robust_relative_v0_no_live_residual.registry.json"))["status"] == "PASS"


def test_t125_terminal_certificate_is_exactly_exhaustion():
    assert check_registry(load("positive/terminal_self_certificate_exhausted.registry.json"))["status"] == "PASS"
    result = check_registry(load("negative/terminal_self_certificate_not_exhausted.registry.json"))
    assert codes(result) == ["TERMINAL_SELF_CERTIFICATE_NOT_EXHAUSTED"]


def test_observer_admissibility_is_not_t125_semantics():
    result = check_registry(load("negative/observer_self_certificate.registry.json"))
    assert codes(result) == ["OBSERVER_CERTIFICATION_SUPPORT_REQUIRED"]
    assert check_registry(load("positive/observer_admissible_certificate.registry.json"))["status"] == "PASS"
