from __future__ import annotations
import copy, importlib.util, json
from pathlib import Path
import pytest
ROOT = Path(__file__).resolve().parents[1]

def load(rel): return json.loads((ROOT / rel).read_text(encoding="utf-8"))
def load_mod():
    p = ROOT / "checker/v0_osap_fc1/cluster_b_wp4.py"
    spec = importlib.util.spec_from_file_location("wp4", p)
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod); return mod
M = load_mod()

def apply_delta(manifest, delta):
    out = copy.deepcopy(manifest); index = {r["theorem_id"]: r for r in out["theorems"]}
    for theorem_id, changes in delta.items():
        for key, value in changes.items():
            if isinstance(value, dict) and isinstance(index[theorem_id].get(key), dict): index[theorem_id][key].update(value)
            else: index[theorem_id][key] = value
    return out

def run_fixture(filename):
    fixture = load("fixtures/gate3/cluster_b/wp4/" + filename)
    proof = apply_delta(load("release/v1.4.0/GATE3_CLUSTER_B_WP4_DUAL_BACKEND_PROOF_MANIFEST.json"), fixture["proof_manifest_delta"])
    return fixture, M.activate_wp3_binding(fixture["binding"], proof)

def test_all_wp4_fixtures_replay_deterministically():
    manifest = load("release/v1.4.0/GATE3_CLUSTER_B_WP4_FIXTURE_MANIFEST.json")
    for item in manifest["fixtures"]:
        fixture = load(item["path"])
        proof = apply_delta(load("release/v1.4.0/GATE3_CLUSTER_B_WP4_DUAL_BACKEND_PROOF_MANIFEST.json"), fixture["proof_manifest_delta"])
        first = M.activate_wp3_binding(fixture["binding"], proof)
        second = M.activate_wp3_binding(fixture["binding"], proof)
        assert first == second
        for key, value in fixture["expected"].items(): assert first[key] == value

def test_pass_requires_both_backends():
    _, out = run_fixture("09_missing_lean_evidence_stays_inconclusive.json")
    assert out["typed_outcome_code"] == "INCONCLUSIVE_UNSUPPORTED_FRAGMENT"
    assert out["certification_claimed"] is False

def test_exact_dual_backend_evidence_activates_certified():
    _, out = run_fixture("01_t157_pass_certifies.json")
    assert out["typed_outcome_code"] == "CERTIFIED"
    assert out["certification_claimed"] is True

def test_parity_failure_has_high_priority_outcome():
    _, out = run_fixture("11_statement_hash_mismatch_is_parity_failure.json")
    assert out["typed_outcome_code"] == "BACKEND_PARITY_FAILURE"

def test_wp3_input_claiming_certification_is_rejected():
    fixture = load("fixtures/gate3/cluster_b/wp4/01_t157_pass_certifies.json")
    binding = copy.deepcopy(fixture["binding"]); binding["certification_claimed"] = True
    with pytest.raises(M.ActivationError): M.activate_wp3_binding(binding, load("release/v1.4.0/GATE3_CLUSTER_B_WP4_DUAL_BACKEND_PROOF_MANIFEST.json"))

def test_theorem_registry_identities_are_preserved():
    wp1 = load("release/v1.4.0/GATE3_CLUSTER_B_WP1_THEOREM_REGISTRY_T157_T162.json")
    wp4 = load("release/v1.4.0/GATE3_CLUSTER_B_WP4_DUAL_BACKEND_PROOF_MANIFEST.json")
    a = {r["theorem_id"]: r for r in wp1["records"]}; b = {r["theorem_id"]: r for r in wp4["theorems"]}
    assert set(a) == set(b) == {"T157", "T158", "T159", "T160", "T161", "T162"}
    for theorem_id in a:
        for key in ("canonical_name", "formal_signature", "statement_sha256", "requires", "conditional", "lean_symbol", "coq_symbol"):
            assert a[theorem_id][key] == b[theorem_id][key]

def test_t158_and_t160_remain_conditional():
    proof = load("release/v1.4.0/GATE3_CLUSTER_B_WP4_DUAL_BACKEND_PROOF_MANIFEST.json")
    index = {r["theorem_id"]: r for r in proof["theorems"]}
    assert index["T158"]["conditional"] is True
    assert index["T160"]["conditional"] is True
