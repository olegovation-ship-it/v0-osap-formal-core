#!/usr/bin/env python3
from __future__ import annotations
import copy, hashlib, importlib.util, json, re, subprocess, sys
from pathlib import Path
from jsonschema import Draft202012Validator
ROOT = Path(__file__).resolve().parents[1]
BASELINE = "c90041d3da5b680b574b910de50d8769d32fbfa9"
THEOREMS = {'T157': {'canonical_name': 'strong_dle_characterization', 'claim_class': 'THEOREM_TARGET', 'conditional': False, 'coq_symbol': 'T157_strong_dle_characterization', 'formal_signature': 'StrongDLE(R,c,r,x,tr) iff WasLive(R,c,r,x) and NoLive(R,c,r,x) and DLETransitionProvenance(tr,c,r,x).', 'lean_symbol': 'V0OSAP.T157_strong_dle_characterization', 'requires': ['T123', 'T132'], 'statement_sha256': '4afc76d031b69016587e0ce65ce3e5d06a3ab9dc864828759ccd94c44889efd2', 'theorem_id': 'T157'}, 'T158': {'canonical_name': 'live_residual_persistence_under_noninterfering_dle', 'claim_class': 'CONDITIONAL_THEOREM_TARGET', 'conditional': True, 'coq_symbol': 'T158_live_residual_persistence_under_noninterfering_dle', 'formal_signature': 'LiveResidual(R0,q) and NonInterferingDLE(tr,q) and Apply(tr,R0)=R1 imply LiveResidual(R1,q).', 'lean_symbol': 'V0OSAP.T158_live_residual_persistence_under_noninterfering_dle', 'requires': ['T124', 'T132', 'T139', 'T162'], 'statement_sha256': '1188ecbe6b4e53ebd061be7350c49aa1d06feb4c9cd270f992ec95e0e170449f', 'theorem_id': 'T158'}, 'T159': {'canonical_name': 'residual_type_separation', 'claim_class': 'THEOREM_TARGET', 'conditional': False, 'coq_symbol': 'T159_residual_type_separation', 'formal_signature': 'ResidualType(q1) != ResidualType(q2) and not AdmissibleTranslation(q1,q2) imply not Interchangeable(q1,q2).', 'lean_symbol': 'V0OSAP.T159_residual_type_separation', 'requires': ['T131', 'T139'], 'statement_sha256': '19478447c22ed4202b7a6c765bf49f019846f209e310a7e18452795d0c46201d', 'theorem_id': 'T159'}, 'T160': {'canonical_name': 'model_pair_noneliminability_witness', 'claim_class': 'CONDITIONAL_THEOREM_TARGET', 'conditional': True, 'coq_symbol': 'T160_model_pair_noneliminability_witness', 'formal_signature': 'AdmissibleModelPair(M1,M2,S) and AgreeOn(M1,M2,S) and LiveResidual(M1,q) != LiveResidual(M2,q) imply NonEliminableFrom(q,S).', 'lean_symbol': 'V0OSAP.T160_model_pair_noneliminability_witness', 'requires': ['T134', 'T135', 'T140', 'T142', 'T159'], 'statement_sha256': '7f78c6738c09425a3aaea7560ce5c21aca1bed9341155de64abb7540d0220f37', 'theorem_id': 'T160'}, 'T161': {'canonical_name': 'minimal_single_residual_obstruction', 'claim_class': 'COROLLARY_TARGET', 'conditional': False, 'coq_symbol': 'T161_minimal_single_residual_obstruction', 'formal_signature': 'DeclaredResidual(q) and LiveResidual(R,q) imply MinimalObstructionWitness(q,RawRelativeV0(R)).', 'lean_symbol': 'V0OSAP.T161_minimal_single_residual_obstruction', 'requires': ['T134'], 'statement_sha256': '2fcb4a46f4f67bfc71b33f01f8f29d4c39f0b1491c4a620387c50da866c6663e', 'theorem_id': 'T161'}, 'T162': {'canonical_name': 'historical_live_token_nonconversion', 'claim_class': 'THEOREM_TARGET', 'conditional': False, 'coq_symbol': 'T162_historical_live_token_nonconversion', 'formal_signature': 'HistoricalToken(t) and not FreshActivation(t,t2) imply not CurrentLiveGuardToken(t2).', 'lean_symbol': 'V0OSAP.T162_historical_live_token_nonconversion', 'requires': ['T133', 'T139'], 'statement_sha256': 'bd9fcaae0841f163733ce3444cfd23407e82de181ffb745b4e434cc00d9bcf4b', 'theorem_id': 'T162'}}

def run(*args, check=True):
    cp = subprocess.run(args, cwd=ROOT, capture_output=True, text=True, check=False)
    if check and cp.returncode: raise SystemExit(f"command failed: {' '.join(args)}\n{cp.stdout}{cp.stderr}")
    return cp

def load(rel): return json.loads((ROOT / rel).read_text(encoding="utf-8"))
def validate(obj, schema_rel):
    errors = sorted(Draft202012Validator(load(schema_rel)).iter_errors(obj), key=lambda e: list(e.path))
    if errors: raise SystemExit(f"schema failure {schema_rel}: {errors[0].message}")
def module():
    p = ROOT / "checker/v0_osap_fc1/cluster_b_wp4.py"
    spec = importlib.util.spec_from_file_location("cluster_b_wp4", p)
    if spec is None or spec.loader is None: raise SystemExit("cannot load WP4 activation module")
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod); return mod

def apply_delta(manifest, delta):
    out = copy.deepcopy(manifest); index = {r["theorem_id"]: r for r in out["theorems"]}
    for theorem_id, changes in delta.items():
        if theorem_id not in index: raise SystemExit("fixture delta theorem unknown")
        for key, value in changes.items():
            if isinstance(value, dict) and isinstance(index[theorem_id].get(key), dict): index[theorem_id][key].update(value)
            else: index[theorem_id][key] = value
    return out

def verify_source_symbols():
    lean = (ROOT / "lean/V0OSAP/ClusterB.lean").read_text(encoding="utf-8")
    coq = (ROOT / "coq/theories/ClusterB.v").read_text(encoding="utf-8")
    for theorem_id, record in THEOREMS.items():
        lean_name = record["lean_symbol"].split(".")[-1]
        coq_name = record["coq_symbol"]
        if len(re.findall(r"\btheorem\s+" + re.escape(lean_name) + r"\b", lean)) != 1: raise SystemExit("Lean symbol coverage failure: " + theorem_id)
        if len(re.findall(r"\bTheorem\s+" + re.escape(coq_name) + r"\b", coq)) != 1: raise SystemExit("Coq symbol coverage failure: " + theorem_id)
    prohibited = [(lean, r"\b(sorry|admit)\b", "Lean"), (coq, r"\b(Admitted|admit)\b", "Coq")]
    for text, pattern, label in prohibited:
        if re.search(pattern, text): raise SystemExit(label + " proof hole detected")

def verify_records():
    pairs = [
        ("release/v1.4.0/GATE3_CLUSTER_B_WP4_BASELINE_LOCK.json", "schemas/v1.4.0/gate3_cluster_b_wp4_baseline_lock.schema.json"),
        ("release/v1.4.0/GATE3_CLUSTER_B_WP4_DUAL_BACKEND_PROOF_MANIFEST.json", "schemas/v1.4.0/gate3_cluster_b_wp4_proof_manifest.schema.json"),
        ("release/v1.4.0/GATE3_CLUSTER_B_WP4_STATEMENT_PARITY_MANIFEST.json", "schemas/v1.4.0/gate3_cluster_b_wp4_parity_manifest.schema.json"),
        ("release/v1.4.0/GATE3_CLUSTER_B_WP4_FIXTURE_MANIFEST.json", "schemas/v1.4.0/gate3_cluster_b_wp4_fixture_manifest.schema.json"),
        ("release/v1.4.0/GATE3_CLUSTER_B_WP4_PRESERVATION_FIREWALL.json", "schemas/v1.4.0/gate3_cluster_b_wp4_preservation_firewall.schema.json"),
        ("release/v1.4.0/GATE3_CLUSTER_B_WP4_ACCEPTANCE_GATES.json", "schemas/v1.4.0/gate3_cluster_b_wp4_acceptance_gates.schema.json"),
        ("release/v1.4.0/GATE3_CLUSTER_B_WP4_SCHEMA_BUNDLE_MANIFEST.json", "schemas/v1.4.0/gate3_cluster_b_wp4_schema_bundle_manifest.schema.json"),
    ]
    for record, schema in pairs: validate(load(record), schema)
    wp1 = load("release/v1.4.0/GATE3_CLUSTER_B_WP1_THEOREM_REGISTRY_T157_T162.json")
    wp1_index = {r["theorem_id"]: r for r in wp1["records"]}
    proof = load("release/v1.4.0/GATE3_CLUSTER_B_WP4_DUAL_BACKEND_PROOF_MANIFEST.json")
    parity = load("release/v1.4.0/GATE3_CLUSTER_B_WP4_STATEMENT_PARITY_MANIFEST.json")
    for record in proof["theorems"]:
        inherited = wp1_index[record["theorem_id"]]
        for key in ("canonical_name", "formal_signature", "statement_sha256", "requires", "conditional", "lean_symbol", "coq_symbol"):
            if record[key] != inherited[key]: raise SystemExit("WP1 theorem identity mutation: " + record["theorem_id"] + ":" + key)
    if parity["coverage_percent"] != 100 or any(r["parity_status"] != "PASS" for r in parity["records"]): raise SystemExit("statement parity incomplete")

def verify_fixtures():
    mod = module(); manifest = load("release/v1.4.0/GATE3_CLUSTER_B_WP4_DUAL_BACKEND_PROOF_MANIFEST.json")
    fixture_manifest = load("release/v1.4.0/GATE3_CLUSTER_B_WP4_FIXTURE_MANIFEST.json")
    for item in fixture_manifest["fixtures"]:
        fixture = load(item["path"]); validate(fixture, "schemas/v1.4.0/gate3_cluster_b_wp4_fixture.schema.json")
        proof = apply_delta(manifest, fixture["proof_manifest_delta"])
        first = mod.activate_wp3_binding(fixture["binding"], proof)
        second = mod.activate_wp3_binding(fixture["binding"], proof)
        if first != second: raise SystemExit("nondeterministic activation: " + fixture["fixture_id"])
        validate(first, "schemas/v1.4.0/gate3_cluster_b_wp4_activation_result.schema.json")
        for key, value in fixture["expected"].items():
            if first.get(key) != value: raise SystemExit(f"fixture {fixture['fixture_id']} mismatch {key}")
        if first["frozen_wp3_binding_modified"] or first["frozen_ipec_v0_1_modified"] or first["release_action_authorized"]: raise SystemExit("activation boundary violated")

def main():
    run(sys.executable, "release/v1.4.0/tools/patch_wp4_allowlist.py", "--check")
    verify_source_symbols(); verify_records(); verify_fixtures()
    cp = run(sys.executable, "scripts/build_gate3_cluster_b_wp4.py", "--check", check=False)
    if cp.returncode: raise SystemExit(cp.stdout + cp.stderr)
    print("WP4 VERIFICATION: PASS")
    return 0
if __name__ == "__main__": raise SystemExit(main())
