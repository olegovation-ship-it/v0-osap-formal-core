#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BASELINE='7b497f197652874164e00fe9c0ef7f67e760c979'
EVIDENCE_INPUT_PATHS=['docs/gate3/cluster_b/BASELINE_AUDIT_AND_BUILD_SPECIFICATION_v0.1.md', 'release/v1.4.0/GATE3_CLUSTER_B_WP0_SCHEMA_BUNDLE_MANIFEST.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP0_POST_MERGE_SHA256SUMS.txt', 'release/v1.4.0/GATE3_CLUSTER_B_WP1_SEMANTIC_ROLE_MAP.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP1_THEOREM_REGISTRY_T157_T162.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP1_DEPENDENCY_DAG.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP1_POST_MERGE_SHA256SUMS.txt', 'release/v1.4.0/GATE3_CLUSTER_B_WP2_FIXTURE_MANIFEST.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP2_SEMANTICS_PROFILE.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP2_POST_MERGE_SHA256SUMS.txt', 'release/v1.4.0/GATE3_CLUSTER_B_WP3_ADAPTER_BINDING_MANIFEST.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP3_EXTENSION_RULE_REGISTRY_T157_T162.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP3_POST_MERGE_SHA256SUMS.txt', 'release/v1.4.0/GATE3_CLUSTER_B_WP4_DUAL_BACKEND_PROOF_MANIFEST.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP4_FIXTURE_MANIFEST.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP4_STATEMENT_PARITY_MANIFEST.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP4_POST_MERGE_FROZEN_UPSTREAM_PRESERVATION_RECORD.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP4_POST_MERGE_SHA256SUMS.txt']
JOB_IDS=['baseline', 'schemas', 'id-audit', 'role-coverage', 'dependency-dag', 'python-semantics', 'positive-models', 'negative-boundary', 'lean', 'coq', 'statement-parity', 'ipec-lineage', 'deterministic-replay', 'gate3-audit-inputs']
GATE_IDS=['WP5-G01', 'WP5-G02', 'WP5-G03', 'WP5-G04', 'WP5-G05', 'WP5-G06', 'WP5-G07', 'WP5-G08', 'WP5-G09', 'WP5-G10', 'WP5-G11', 'WP5-G12', 'WP5-G13', 'WP5-G14', 'WP5-G15', 'WP5-G16', 'WP5-G17', 'WP5-G18', 'WP5-G19', 'WP5-G20', 'WP5-G21', 'WP5-G22', 'WP5-G23', 'WP5-G24']
THEOREMS=['T123', 'T124', 'T126', 'T132', 'T134', 'T135', 'T136', 'T139', 'T140', 'T142', 'T157', 'T158', 'T159', 'T160', 'T161', 'T162']
ROLES=['CB-R1', 'CB-R2', 'CB-R3', 'CB-R4', 'CB-R5', 'CB-R6', 'CB-R7']
def run_bytes(*args: str) -> bytes:
    cp=subprocess.run(args,cwd=ROOT,capture_output=True,check=False)
    if cp.returncode: raise SystemExit(cp.stderr.decode('utf-8',errors='replace'))
    return cp.stdout
def sha(data: bytes) -> str: return hashlib.sha256(data).hexdigest()
def canonical(obj) -> bytes: return json.dumps(obj,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode('utf-8')
def evidence_inputs():
    out=[]
    for rel in sorted(EVIDENCE_INPUT_PATHS):
        historical=run_bytes('git','show',f'{BASELINE}:{rel}')
        current=(ROOT/rel).read_bytes()
        if current!=historical: raise SystemExit('frozen evidence input differs from baseline: '+rel)
        out.append({'path':rel,'sha256':sha(historical),'source_commit':BASELINE})
    return out
def build_bundle(inputs):
    return {'baseline_commit':BASELINE,'evidence_inputs':inputs,'ci_job_ids':JOB_IDS,'acceptance_gate_ids':GATE_IDS,'theorem_ids':THEOREMS,'semantic_role_ids':ROLES,'release_authorization':'NONE','wp6_decision':'NOT_PERFORMED'}
def validate_candidate(candidate: dict, expected_inputs: list[dict]):
    if candidate.get('release_authorization')!='NONE': return 'REJECT','RELEASE_ACTION_FORBIDDEN'
    if candidate.get('baseline_commit')!=BASELINE: return 'REJECT','PREDECESSOR_CHAIN_MISMATCH'
    paths=[x.get('path') for x in candidate.get('evidence_inputs',[])]
    if len(paths)!=len(set(paths)): return 'REJECT','EVIDENCE_PATH_DUPLICATE'
    if paths!=sorted(paths): return 'REJECT','EVIDENCE_PATH_ORDER_INVALID'
    expected={x['path']:x['sha256'] for x in expected_inputs}
    if set(paths)!=set(expected) or len(paths)!=len(expected): return 'REJECT','EVIDENCE_PATH_SET_MISMATCH'
    for row in candidate.get('evidence_inputs',[]):
        if expected.get(row.get('path'))!=row.get('sha256'): return 'REJECT','EVIDENCE_SHA256_MISMATCH'
    return 'PASS','NONE'
def mutate(base: dict, mutation: str):
    obj=json.loads(json.dumps(base))
    if mutation=='REVERSE_PATH_ORDER': obj['evidence_inputs']=list(reversed(obj['evidence_inputs']))
    elif mutation=='DUPLICATE_FIRST_PATH': obj['evidence_inputs'].append(dict(obj['evidence_inputs'][0]))
    elif mutation=='MUTATE_FIRST_SHA256': obj['evidence_inputs'][0]['sha256']='0'*64
    elif mutation=='MUTATE_BASELINE_COMMIT': obj['baseline_commit']='0'*40
    elif mutation=='AUTHORIZE_RELEASE_ACTION': obj['release_authorization']='AUTHORIZED'
    elif mutation!='NONE': raise SystemExit('unknown mutation '+mutation)
    return obj
def main() -> int:
    p=argparse.ArgumentParser(); p.add_argument('--emit-bundle'); p.add_argument('--fixture'); a=p.parse_args()
    inputs=evidence_inputs(); bundle=build_bundle(inputs); data1=canonical(bundle); data2=canonical(build_bundle(evidence_inputs()))
    if data1!=data2: raise SystemExit('replay bytes differ')
    if a.fixture:
        f=json.loads((ROOT/a.fixture).read_text()); candidate=mutate(bundle,f['mutation']); status,diag=validate_candidate(candidate,inputs)
        print(json.dumps({'status':status,'diagnostic':diag},sort_keys=True));
        return 0 if (status==f['expected_status'] and diag==f['expected_diagnostic']) else 1
    if a.emit_bundle: Path(a.emit_bundle).write_bytes(data1)
    print(json.dumps({'status':'PASS','sha256':sha(data1),'size_bytes':len(data1),'byte_identical':True},sort_keys=True))
    return 0
if __name__=='__main__': raise SystemExit(main())
