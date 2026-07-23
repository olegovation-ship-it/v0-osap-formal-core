#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, sys
from pathlib import Path
from jsonschema import Draft202012Validator
ROOT = Path(__file__).resolve().parents[1]
BASELINE = "c90041d3da5b680b574b910de50d8769d32fbfa9"
LOCKED = {'T157': {'conditional': False, 'coq_symbol': 'T157_strong_dle_characterization', 'formal_signature': 'StrongDLE(R,c,r,x,tr) iff WasLive(R,c,r,x) and NoLive(R,c,r,x) and DLETransitionProvenance(tr,c,r,x).', 'lean_symbol': 'V0OSAP.T157_strong_dle_characterization', 'requires': ['T123', 'T132'], 'statement_sha256': '4afc76d031b69016587e0ce65ce3e5d06a3ab9dc864828759ccd94c44889efd2'}, 'T158': {'conditional': True, 'coq_symbol': 'T158_live_residual_persistence_under_noninterfering_dle', 'formal_signature': 'LiveResidual(R0,q) and NonInterferingDLE(tr,q) and Apply(tr,R0)=R1 imply LiveResidual(R1,q).', 'lean_symbol': 'V0OSAP.T158_live_residual_persistence_under_noninterfering_dle', 'requires': ['T124', 'T132', 'T139', 'T162'], 'statement_sha256': '1188ecbe6b4e53ebd061be7350c49aa1d06feb4c9cd270f992ec95e0e170449f'}, 'T159': {'conditional': False, 'coq_symbol': 'T159_residual_type_separation', 'formal_signature': 'ResidualType(q1) != ResidualType(q2) and not AdmissibleTranslation(q1,q2) imply not Interchangeable(q1,q2).', 'lean_symbol': 'V0OSAP.T159_residual_type_separation', 'requires': ['T131', 'T139'], 'statement_sha256': '19478447c22ed4202b7a6c765bf49f019846f209e310a7e18452795d0c46201d'}, 'T160': {'conditional': True, 'coq_symbol': 'T160_model_pair_noneliminability_witness', 'formal_signature': 'AdmissibleModelPair(M1,M2,S) and AgreeOn(M1,M2,S) and LiveResidual(M1,q) != LiveResidual(M2,q) imply NonEliminableFrom(q,S).', 'lean_symbol': 'V0OSAP.T160_model_pair_noneliminability_witness', 'requires': ['T134', 'T135', 'T140', 'T142', 'T159'], 'statement_sha256': '7f78c6738c09425a3aaea7560ce5c21aca1bed9341155de64abb7540d0220f37'}, 'T161': {'conditional': False, 'coq_symbol': 'T161_minimal_single_residual_obstruction', 'formal_signature': 'DeclaredResidual(q) and LiveResidual(R,q) imply MinimalObstructionWitness(q,RawRelativeV0(R)).', 'lean_symbol': 'V0OSAP.T161_minimal_single_residual_obstruction', 'requires': ['T134'], 'statement_sha256': '2fcb4a46f4f67bfc71b33f01f8f29d4c39f0b1491c4a620387c50da866c6663e'}, 'T162': {'conditional': False, 'coq_symbol': 'T162_historical_live_token_nonconversion', 'formal_signature': 'HistoricalToken(t) and not FreshActivation(t,t2) imply not CurrentLiveGuardToken(t2).', 'lean_symbol': 'V0OSAP.T162_historical_live_token_nonconversion', 'requires': ['T133', 'T139'], 'statement_sha256': 'bd9fcaae0841f163733ce3444cfd23407e82de181ffb745b4e434cc00d9bcf4b'}}
SCHEMA_PAIRS = [
    ("release/v1.4.0/GATE3_CLUSTER_B_WP4_BASELINE_LOCK.json", "schemas/v1.4.0/gate3_cluster_b_wp4_baseline_lock.schema.json"),
    ("release/v1.4.0/GATE3_CLUSTER_B_WP4_DUAL_BACKEND_PROOF_MANIFEST.json", "schemas/v1.4.0/gate3_cluster_b_wp4_proof_manifest.schema.json"),
    ("release/v1.4.0/GATE3_CLUSTER_B_WP4_STATEMENT_PARITY_MANIFEST.json", "schemas/v1.4.0/gate3_cluster_b_wp4_parity_manifest.schema.json"),
    ("release/v1.4.0/GATE3_CLUSTER_B_WP4_FIXTURE_MANIFEST.json", "schemas/v1.4.0/gate3_cluster_b_wp4_fixture_manifest.schema.json"),
    ("release/v1.4.0/GATE3_CLUSTER_B_WP4_PRESERVATION_FIREWALL.json", "schemas/v1.4.0/gate3_cluster_b_wp4_preservation_firewall.schema.json"),
    ("release/v1.4.0/GATE3_CLUSTER_B_WP4_ACCEPTANCE_GATES.json", "schemas/v1.4.0/gate3_cluster_b_wp4_acceptance_gates.schema.json"),
    ("release/v1.4.0/GATE3_CLUSTER_B_WP4_SCHEMA_BUNDLE_MANIFEST.json", "schemas/v1.4.0/gate3_cluster_b_wp4_schema_bundle_manifest.schema.json"),
]
LEDGER = ROOT / "release/v1.4.0/GATE3_CLUSTER_B_WP4_SHA256SUMS.txt"

def load(rel): return json.loads((ROOT / rel).read_text(encoding="utf-8"))
def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def normalized_hash(signature): return hashlib.sha256(" ".join(signature.split()).encode("utf-8")).hexdigest()
def validate(obj, schema_rel):
    errors = sorted(Draft202012Validator(load(schema_rel)).iter_errors(obj), key=lambda e: list(e.path))
    if errors: raise SystemExit(f"schema failure {schema_rel}: {errors[0].message}")
def wp4_paths():
    paths = []
    exact = [
        ".github/workflows/gate3-cluster-b-wp4.yml", "checker/v0_osap_fc1/cluster_b_wp4.py",
        "lean/V0OSAP/ClusterB.lean", "coq/theories/ClusterB.v",
        "lean/V0OSAP.lean", "lean/V0OSAP/Theorems.lean", "coq/_CoqProject", "coq/theories/Theorems.v",
        "scripts/build_gate3_cluster_b_wp4.py", "scripts/verify_gate3_cluster_b_wp4.py",
        "pytest.ini", "tests/test_gate3_cluster_b_wp4.py", "release/v1.4.0/tools/patch_wp4_allowlist.py",
    ]
    paths.extend(exact)
    for prefix in ["docs/gate3/cluster_b/WP4_", "fixtures/gate3/cluster_b/wp4/", "release/v1.4.0/GATE3_CLUSTER_B_WP4_", "schemas/v1.4.0/gate3_cluster_b_wp4_"]:
        base = ROOT / prefix.rsplit("/", 1)[0]
        if base.exists():
            paths.extend(p.relative_to(ROOT).as_posix() for p in base.rglob("*") if p.is_file() and p.relative_to(ROOT).as_posix().startswith(prefix))
    return sorted(set(p for p in paths if p != "release/v1.4.0/GATE3_CLUSTER_B_WP4_SHA256SUMS.txt"))
def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--check", action="store_true"); args = ap.parse_args()
    for record_rel, schema_rel in SCHEMA_PAIRS: validate(load(record_rel), schema_rel)
    proof = load("release/v1.4.0/GATE3_CLUSTER_B_WP4_DUAL_BACKEND_PROOF_MANIFEST.json")
    parity = load("release/v1.4.0/GATE3_CLUSTER_B_WP4_STATEMENT_PARITY_MANIFEST.json")
    proof_index = {r["theorem_id"]: r for r in proof["theorems"]}
    parity_index = {r["theorem_id"]: r for r in parity["records"]}
    if set(proof_index) != set(LOCKED) or set(parity_index) != set(LOCKED): raise SystemExit("theorem coverage mismatch")
    for theorem_id, locked in LOCKED.items():
        p = proof_index[theorem_id]; q = parity_index[theorem_id]
        if p["formal_signature"] != locked["formal_signature"] or q["formal_signature"] != locked["formal_signature"]: raise SystemExit("signature mutation: " + theorem_id)
        if normalized_hash(locked["formal_signature"]) != locked["statement_sha256"]: raise SystemExit("locked hash mismatch: " + theorem_id)
        if p["statement_sha256"] != locked["statement_sha256"] or q["statement_sha256"] != locked["statement_sha256"]: raise SystemExit("statement hash mutation: " + theorem_id)
        if p["requires"] != locked["requires"] or q["dependency_ids"] != locked["requires"]: raise SystemExit("dependency mutation: " + theorem_id)
        if p["conditional"] is not locked["conditional"] or q["conditional"] is not locked["conditional"]: raise SystemExit("conditionality mutation: " + theorem_id)
        if p["lean"]["symbol"] != locked["lean_symbol"] or p["coq"]["symbol"] != locked["coq_symbol"]: raise SystemExit("symbol mutation: " + theorem_id)
    fixture_manifest = load("release/v1.4.0/GATE3_CLUSTER_B_WP4_FIXTURE_MANIFEST.json")
    for item in fixture_manifest["fixtures"]:
        fixture = load(item["path"]); validate(fixture, "schemas/v1.4.0/gate3_cluster_b_wp4_fixture.schema.json")
    lines = []
    for rel in wp4_paths():
        path = ROOT / rel
        if not path.is_file(): raise SystemExit("missing WP4 path: " + rel)
        lines.append(f"{digest(path)}  {rel}")
    expected = "\n".join(lines) + "\n"
    if args.check:
        if not LEDGER.is_file() or LEDGER.read_text(encoding="utf-8") != expected: raise SystemExit("WP4 SHA-256 ledger mismatch")
    else:
        LEDGER.write_text(expected, encoding="utf-8", newline="\n")
    print("WP4 BUILD: PASS")
    return 0
if __name__ == "__main__": raise SystemExit(main())
