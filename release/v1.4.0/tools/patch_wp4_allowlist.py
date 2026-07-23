#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json, subprocess, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
BASELINE = 'c90041d3da5b680b574b910de50d8769d32fbfa9'
MODIFIED = ['coq/_CoqProject', 'coq/theories/Theorems.v', 'lean/V0OSAP.lean', 'lean/V0OSAP/Theorems.lean']
PRE = {'lean/V0OSAP.lean': '3d41f76ed4ba28dca11c3454e86b35f7a0f6c6cdbaa6116af43609d4ef9201f5', 'lean/V0OSAP/Theorems.lean': 'e9c6ca2b998b6af095ea0b0ae31c9b6b8b1a61f914e9c04a32db39d1c69cc290', 'coq/_CoqProject': '14654d8194a06cf460cdba6b2ade125c8c63488dd35eddf68e6325e7b8cedbaa', 'coq/theories/Theorems.v': '6fb52e2ee838190398cd53ce820a11cea199ebcefc39512670c2de43a40fc5b5'}
POST = {'lean/V0OSAP.lean': '696a1b85fb78518d6826c2efbca6a21f8f9707454fa6367020a8db8c4bd246f0', 'lean/V0OSAP/Theorems.lean': '65302fd57502cfaa89bb71644e35c10d23b31d5a20a3d5bc63e7b9e1bece799e', 'coq/_CoqProject': '476abaf801f06377b859aa2e4b0b3bc07f059a9085221a714f7073885b8b26dd', 'coq/theories/Theorems.v': '8d5453e077179e3401c3f51ebeecc864ef81eaf275398c536ab303cf5e994883'}
NEW = ['.github/workflows/gate3-cluster-b-wp4.yml', 'checker/v0_osap_fc1/cluster_b_wp4.py', 'coq/theories/ClusterB.v', 'docs/gate3/cluster_b/WP4_BUILD_SPECIFICATION.md', 'docs/gate3/cluster_b/WP4_LEAN_COQ_PROOF_COMPLETION_AND_STATEMENT_PARITY.md', 'fixtures/gate3/cluster_b/wp4/01_t157_pass_certifies.json', 'fixtures/gate3/cluster_b/wp4/02_t158_t162_pass_certifies.json', 'fixtures/gate3/cluster_b/wp4/03_t159_rejection_activates.json', 'fixtures/gate3/cluster_b/wp4/04_t160_rejection_activates.json', 'fixtures/gate3/cluster_b/wp4/05_t161_pass_certifies.json', 'fixtures/gate3/cluster_b/wp4/06_t162_pass_certifies.json', 'fixtures/gate3/cluster_b/wp4/07_inherited_rejection_preserved.json', 'fixtures/gate3/cluster_b/wp4/08_source_deferred_stays_inconclusive.json', 'fixtures/gate3/cluster_b/wp4/09_missing_lean_evidence_stays_inconclusive.json', 'fixtures/gate3/cluster_b/wp4/10_missing_coq_evidence_stays_inconclusive.json', 'fixtures/gate3/cluster_b/wp4/11_statement_hash_mismatch_is_parity_failure.json', 'fixtures/gate3/cluster_b/wp4/12_backend_parity_false_is_failure.json', 'lean/V0OSAP/ClusterB.lean', 'pytest.ini', 'release/v1.4.0/GATE3_CLUSTER_B_WP4_ACCEPTANCE_GATES.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP4_BASELINE_LOCK.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP4_DUAL_BACKEND_PROOF_MANIFEST.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP4_FIXTURE_MANIFEST.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP4_PRESERVATION_FIREWALL.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP4_SCHEMA_BUNDLE_MANIFEST.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP4_SHA256SUMS.txt', 'release/v1.4.0/GATE3_CLUSTER_B_WP4_STATEMENT_PARITY_MANIFEST.json', 'release/v1.4.0/tools/patch_wp4_allowlist.py', 'schemas/v1.4.0/gate3_cluster_b_wp4_acceptance_gates.schema.json', 'schemas/v1.4.0/gate3_cluster_b_wp4_activation_result.schema.json', 'schemas/v1.4.0/gate3_cluster_b_wp4_baseline_lock.schema.json', 'schemas/v1.4.0/gate3_cluster_b_wp4_fixture.schema.json', 'schemas/v1.4.0/gate3_cluster_b_wp4_fixture_manifest.schema.json', 'schemas/v1.4.0/gate3_cluster_b_wp4_parity_manifest.schema.json', 'schemas/v1.4.0/gate3_cluster_b_wp4_preservation_firewall.schema.json', 'schemas/v1.4.0/gate3_cluster_b_wp4_proof_manifest.schema.json', 'schemas/v1.4.0/gate3_cluster_b_wp4_schema_bundle_manifest.schema.json', 'scripts/build_gate3_cluster_b_wp4.py', 'scripts/verify_gate3_cluster_b_wp4.py', 'tests/test_gate3_cluster_b_wp4.py']
EXPECTED = set(MODIFIED) | set(NEW)

def run(*args, check=True, text=True):
    cp = subprocess.run(args, cwd=ROOT, capture_output=True, text=text, check=False)
    if check and cp.returncode:
        raise SystemExit(f"command failed: {' '.join(args)}\n{cp.stdout}{cp.stderr}")
    return cp

def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def lines(*args): return [x for x in run('git', *args).stdout.splitlines() if x]

def main():
    run('git', 'cat-file', '-e', BASELINE + '^{commit}')
    head = run('git', 'rev-parse', 'HEAD').stdout.strip()
    if head != BASELINE: run('git', 'merge-base', '--is-ancestor', BASELINE, head)
    changed = set(lines('diff', '--name-only', BASELINE, '--'))
    changed.update(lines('ls-files', '--others', '--exclude-standard'))
    if changed != EXPECTED:
        raise SystemExit('FAIL_WP4_ALLOWLIST missing=' + str(sorted(EXPECTED-changed)) + ', extra=' + str(sorted(changed-EXPECTED)))
    for row in lines('diff', '--name-status', BASELINE, '--'):
        code, path = row.split('\t', 1)
        if path in MODIFIED and code != 'M': raise SystemExit('modified path status mismatch: ' + row)
        if path in NEW and code != 'A': raise SystemExit('new path status mismatch: ' + row)
    for rel in MODIFIED:
        historical = run('git', 'show', f'{BASELINE}:{rel}', text=False).stdout
        if hashlib.sha256(historical).hexdigest() != PRE[rel]: raise SystemExit('baseline pre-hash mismatch: ' + rel)
        current = ROOT / rel
        if not current.is_file() or digest(current) != POST[rel]: raise SystemExit('post-hash mismatch: ' + rel)
    for rel in lines('ls-tree', '-r', '--name-only', BASELINE):
        if rel in MODIFIED: continue
        current = ROOT / rel
        if not current.is_file(): raise SystemExit('missing frozen baseline path: ' + rel)
        historical = run('git', 'show', f'{BASELINE}:{rel}', text=False).stdout
        if current.read_bytes() != historical: raise SystemExit('modified frozen baseline path: ' + rel)
    forbidden_prefixes = (
        'release/v1.4.0/GATE3_CLUSTER_B_WP0_', 'release/v1.4.0/GATE3_CLUSTER_B_WP1_',
        'release/v1.4.0/GATE3_CLUSTER_B_WP2_', 'release/v1.4.0/GATE3_CLUSTER_B_WP3_',
        'docs/gate3/cluster_b/WP0_', 'docs/gate3/cluster_b/WP1_', 'docs/gate3/cluster_b/WP2_', 'docs/gate3/cluster_b/WP3_'
    )
    if any(path.startswith(forbidden_prefixes) for path in changed): raise SystemExit('frozen WP0-WP3 path changed')
    print('WP4 EXACT CHANGED-PATH ALLOWLIST: PASS')
    return 0
if __name__ == '__main__': raise SystemExit(main())
