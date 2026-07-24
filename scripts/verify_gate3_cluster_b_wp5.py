#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def run(*a,check=True):
    cp=subprocess.run(a,cwd=ROOT,capture_output=True,text=True,check=False)
    if check and cp.returncode: raise SystemExit(cp.stdout+cp.stderr)
    return cp
def load(r): return json.loads((ROOT/r).read_text(encoding='utf-8'))
def main():
    p=argparse.ArgumentParser(); p.add_argument('--job',default='full'); p.parse_args()
    run('python','release/v1.4.0/tools/patch_wp5_allowlist.py','--check')
    run('python','scripts/build_gate3_cluster_b_wp5.py','--check')
    gates=load('release/v1.4.0/GATE3_CLUSTER_B_WP5_ACCEPTANCE_GATES.json')
    if gates['gate_count']!=24 or gates['close_gate3_authorized'] or gates['release_authorization']!='NONE':
        raise SystemExit('WP5 acceptance boundary failure')
    plan=load('release/v1.4.0/GATE3_CLUSTER_B_WP5_BUILD_PLAN.json')
    if plan['new_theorem_ids'] or len(plan['semantic_role_ids'])!=7: raise SystemExit('WP5 scope mutation')
    dag=load('release/v1.4.0/GATE3_CLUSTER_B_WP1_DEPENDENCY_DAG.json')
    if dag['cluster_node_count']!=16 or dag['status']!='ACYCLIC_DEPENDENCIES_DECLARED': raise SystemExit('DAG preservation failure')
    binding=load('release/v1.4.0/GATE3_CLUSTER_B_WP3_ADAPTER_BINDING_MANIFEST.json')
    if binding['binding_count']!=9: raise SystemExit('WP3 lineage preservation failure')
    parity=load('release/v1.4.0/GATE3_CLUSTER_B_WP4_STATEMENT_PARITY_MANIFEST.json')
    if parity['coverage_percent']!=100: raise SystemExit('statement parity failure')
    proof=load('release/v1.4.0/GATE3_CLUSTER_B_WP4_DUAL_BACKEND_PROOF_MANIFEST.json')
    if proof['theorem_count']!=6 or any(r['lean']['status']!='PROVED' or r['coq']['status']!='PROVED' for r in proof['theorems']):
        raise SystemExit('dual-backend proof preservation failure')
    replay=load('release/v1.4.0/GATE3_CLUSTER_B_WP5_REPLAY_RECORD.json')
    if not replay['byte_identical'] or replay['run_1_sha256']!=replay['run_2_sha256']: raise SystemExit('replay failure')
    print('WP5 RESULT: READY_FOR_WP6_AUDIT (NO GATE3 DECISION)')
    print(json.dumps({'artifact':'V0_OSAP_GATE3_CLUSTER_B_WP5','status':'PASS','release_authorized':False,'wp6_decision_performed':False},indent=2,sort_keys=True))
    return 0
if __name__=='__main__': raise SystemExit(main())
