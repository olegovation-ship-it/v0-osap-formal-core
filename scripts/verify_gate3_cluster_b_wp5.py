#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, os, subprocess, tempfile
from pathlib import Path
from jsonschema import Draft202012Validator
ROOT=Path(__file__).resolve().parents[1]
BASELINE='7b497f197652874164e00fe9c0ef7f67e760c979'; BRANCH='v1.4.0-development'; TAG_TARGET='13bf095688bcabd5b090f188e9bd28a16237edeb'
EVIDENCE_INPUT_PATHS=['docs/gate3/cluster_b/BASELINE_AUDIT_AND_BUILD_SPECIFICATION_v0.1.md', 'release/v1.4.0/GATE3_CLUSTER_B_WP0_SCHEMA_BUNDLE_MANIFEST.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP0_POST_MERGE_SHA256SUMS.txt', 'release/v1.4.0/GATE3_CLUSTER_B_WP1_SEMANTIC_ROLE_MAP.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP1_THEOREM_REGISTRY_T157_T162.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP1_DEPENDENCY_DAG.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP1_POST_MERGE_SHA256SUMS.txt', 'release/v1.4.0/GATE3_CLUSTER_B_WP2_FIXTURE_MANIFEST.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP2_SEMANTICS_PROFILE.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP2_POST_MERGE_SHA256SUMS.txt', 'release/v1.4.0/GATE3_CLUSTER_B_WP3_ADAPTER_BINDING_MANIFEST.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP3_EXTENSION_RULE_REGISTRY_T157_T162.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP3_POST_MERGE_SHA256SUMS.txt', 'release/v1.4.0/GATE3_CLUSTER_B_WP4_DUAL_BACKEND_PROOF_MANIFEST.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP4_FIXTURE_MANIFEST.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP4_STATEMENT_PARITY_MANIFEST.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP4_POST_MERGE_FROZEN_UPSTREAM_PRESERVATION_RECORD.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP4_POST_MERGE_SHA256SUMS.txt']
EXPECTED_JOB_IDS=['baseline', 'schemas', 'id-audit', 'role-coverage', 'dependency-dag', 'python-semantics', 'positive-models', 'negative-boundary', 'lean', 'coq', 'statement-parity', 'ipec-lineage', 'deterministic-replay', 'gate3-audit-inputs']
EXPECTED_THEOREMS={'T123','T124','T126','T132','T134','T135','T136','T139','T140','T142'}|{f'T{i}' for i in range(157,163)}
def load(rel): return json.loads((ROOT/rel).read_text(encoding='utf-8'))
def run(*args: str, check: bool=True, cwd: Path|None=None):
    cp=subprocess.run(args,cwd=cwd or ROOT,capture_output=True,text=True,check=False)
    if check and cp.returncode: raise SystemExit(cp.stdout+cp.stderr)
    return cp
def lines(*args: str): return [x for x in run('git',*args).stdout.splitlines() if x]
def digest(p: Path): return hashlib.sha256(p.read_bytes()).hexdigest()
def canonical(obj): return json.dumps(obj,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode('utf-8')
def baseline_job():
    branch=run('git','branch','--show-current',check=False).stdout.strip() or os.environ.get('GITHUB_HEAD_REF','') or os.environ.get('GITHUB_REF_NAME','')
    if branch and branch not in (BRANCH,'main') and os.environ.get('GITHUB_ACTIONS')!='true': raise SystemExit('unexpected branch '+repr(branch))
    head=run('git','rev-parse','HEAD').stdout.strip()
    if run('git','merge-base','--is-ancestor',BASELINE,head,check=False).returncode: raise SystemExit('WP5 baseline is not an ancestor of HEAD')
    if os.environ.get('GITHUB_ACTIONS')!='true':
        if head!=BASELINE: raise SystemExit('local HEAD is not the pinned WP5 baseline')
        for ref in ('origin/main','origin/'+BRANCH):
            if run('git','rev-parse',ref).stdout.strip()!=BASELINE: raise SystemExit(ref+' mismatch')
    if run('git','rev-parse','refs/tags/v1.3.0^{}').stdout.strip()!=TAG_TARGET: raise SystemExit('stable tag target changed')
    run('python','release/v1.4.0/tools/patch_wp5_allowlist.py','--check')
    firewall=load('release/v1.4.0/GATE3_CLUSTER_B_WP5_PRESERVATION_FIREWALL.json')
    baseline_paths=set(lines('ls-tree','-r','--name-only',BASELINE))
    for rel in sorted(baseline_paths):
        if rel in firewall['frozen_exact_paths'] or any(rel.startswith(p) for p in firewall['frozen_prefixes']):
            hist=run('git','show',f'{BASELINE}:{rel}',check=True).stdout.encode('utf-8')
            # Text files are used by this repository-boundary. Compare bytes through git show in binary mode when needed.
            cp=subprocess.run(['git','show',f'{BASELINE}:{rel}'],cwd=ROOT,capture_output=True,check=True)
            if not (ROOT/rel).is_file() or (ROOT/rel).read_bytes()!=cp.stdout: raise SystemExit('frozen predecessor path changed '+rel)
def schemas_job():
    run('python','scripts/build_gate3_cluster_b_wp5.py','--check')
    pairs=[('release/v1.4.0/GATE3_CLUSTER_B_WP5_BUILD_PLAN.json', 'schemas/v1.4.0/gate3_cluster_b_wp5_build_plan.schema.json'), ('release/v1.4.0/GATE3_CLUSTER_B_WP5_BASELINE_LOCK.json', 'schemas/v1.4.0/gate3_cluster_b_wp5_baseline_lock.schema.json'), ('release/v1.4.0/GATE3_CLUSTER_B_WP5_CI_JOB_MATRIX.json', 'schemas/v1.4.0/gate3_cluster_b_wp5_ci_job_matrix.schema.json'), ('release/v1.4.0/GATE3_CLUSTER_B_WP5_EVIDENCE_INPUT_MANIFEST.json', 'schemas/v1.4.0/gate3_cluster_b_wp5_evidence_input_manifest.schema.json'), ('release/v1.4.0/GATE3_CLUSTER_B_WP5_FIXTURE_MANIFEST.json', 'schemas/v1.4.0/gate3_cluster_b_wp5_fixture_manifest.schema.json'), ('release/v1.4.0/GATE3_CLUSTER_B_WP5_PRESERVATION_FIREWALL.json', 'schemas/v1.4.0/gate3_cluster_b_wp5_preservation_firewall.schema.json'), ('release/v1.4.0/GATE3_CLUSTER_B_WP5_REPLAY_RECORD.json', 'schemas/v1.4.0/gate3_cluster_b_wp5_replay_record.schema.json'), ('release/v1.4.0/GATE3_CLUSTER_B_WP5_ACCEPTANCE_GATES.json', 'schemas/v1.4.0/gate3_cluster_b_wp5_acceptance_gates.schema.json'), ('release/v1.4.0/GATE3_CLUSTER_B_WP5_SCHEMA_BUNDLE_MANIFEST.json', 'schemas/v1.4.0/gate3_cluster_b_wp5_schema_bundle_manifest.schema.json')]
    for doc,sch in pairs:
        errs=sorted(Draft202012Validator(load(sch)).iter_errors(load(doc)),key=lambda e:list(e.path))
        if errs: raise SystemExit('schema failure '+doc+': '+errs[0].message)
    evidence=load('release/v1.4.0/GATE3_CLUSTER_B_WP5_EVIDENCE_INPUT_MANIFEST.json')
    paths=[r['path'] for r in evidence['inputs']]
    if evidence['input_count']!=len(EVIDENCE_INPUT_PATHS) or paths!=sorted(EVIDENCE_INPUT_PATHS) or len(paths)!=len(set(paths)): raise SystemExit('evidence input path set/order mismatch')
    for row in evidence['inputs']:
        cp=subprocess.run(['git','show',f'{BASELINE}:{row["path"]}'],cwd=ROOT,capture_output=True,check=True)
        if hashlib.sha256(cp.stdout).hexdigest()!=row['sha256'] or (ROOT/row['path']).read_bytes()!=cp.stdout: raise SystemExit('evidence input digest/baseline mismatch '+row['path'])
    cp=json.loads(json.dumps(evidence)); cp['canonical_sha256']=None
    if hashlib.sha256(canonical(cp)).hexdigest()!=evidence['canonical_sha256']: raise SystemExit('evidence manifest canonical hash mismatch')
    fm=load('release/v1.4.0/GATE3_CLUSTER_B_WP5_FIXTURE_MANIFEST.json'); fs=load('schemas/v1.4.0/gate3_cluster_b_wp5_evidence_fixture.schema.json')
    if fm['fixture_count']!=6 or len(fm['fixtures'])!=6: raise SystemExit('evidence fixture count mismatch')
    seen=set()
    for row in fm['fixtures']:
        if row['path'] in seen: raise SystemExit('duplicate fixture path '+row['path'])
        seen.add(row['path']); fixture=load(row['path'])
        errs=sorted(Draft202012Validator(fs).iter_errors(fixture),key=lambda e:list(e.path))
        if errs: raise SystemExit('fixture schema failure '+row['path']+': '+errs[0].message)
        if digest(ROOT/row['path'])!=row['sha256'] or fixture['fixture_id']!=row['fixture_id']: raise SystemExit('fixture manifest integrity failure '+row['path'])
    matrix=load('release/v1.4.0/GATE3_CLUSTER_B_WP5_CI_JOB_MATRIX.json')
    ids=[r['job_id'] for r in matrix['jobs']]
    if matrix['job_count']!=14 or ids!=EXPECTED_JOB_IDS or len(ids)!=len(set(ids)) or matrix['permissions']!='CONTENTS_READ_ONLY': raise SystemExit('WP5 CI matrix identity/read-only failure')
    if any((not r['mandatory']) or r['release_capability'] for r in matrix['jobs']): raise SystemExit('WP5 CI job authorization failure')
def id_job():
    reg=load('release/v1.4.0/GATE3_CLUSTER_B_WP1_THEOREM_REGISTRY_T157_T162.json')
    ids={r['theorem_id'] for r in reg['records']}
    if ids!={f'T{i}' for i in range(157,163)}: raise SystemExit('T157-T162 identity coverage failure')
    plan=load('release/v1.4.0/GATE3_CLUSTER_B_WP5_BUILD_PLAN.json')
    if plan['new_theorem_ids'] or set(plan['inherited_cluster_theorem_ids']+plan['locked_extension_theorem_ids'])!=EXPECTED_THEOREMS: raise SystemExit('WP5 theorem scope mutation')
def role_job():
    role=load('release/v1.4.0/GATE3_CLUSTER_B_WP1_SEMANTIC_ROLE_MAP.json')
    if role['required_role_count']!=7 or {r['role_id'] for r in role['roles']}!={f'CB-R{i}' for i in range(1,8)}: raise SystemExit('semantic role coverage failure')
def dag_job():
    dag=load('release/v1.4.0/GATE3_CLUSTER_B_WP1_DEPENDENCY_DAG.json')
    nodes={r['theorem_id']:r['requires'] for r in dag['nodes']}; external={r['theorem_id'] for r in dag['external_dependencies']}
    if len(nodes)!=16 or set(nodes)!=EXPECTED_THEOREMS: raise SystemExit('cluster DAG node set mismatch')
    seen=set()
    for n in dag['topological_order']:
        if n in nodes:
            bad=[d for d in nodes[n] if d in nodes and d not in seen]
            if bad: raise SystemExit('dependency order violation '+n+':'+repr(bad))
            seen.add(n)
    if seen!=set(nodes): raise SystemExit('DAG topological coverage mismatch')
def model_counts():
    m=load('release/v1.4.0/GATE3_CLUSTER_B_WP2_FIXTURE_MANIFEST.json'); statuses=[r['status'] for r in m['fixtures']]
    return statuses.count('PASS'), sum(x in ('REJECT','DEFERRED') for x in statuses)
def positive_job():
    p,_=model_counts()
    if p<12: raise SystemExit('positive model target not met')
def negative_job():
    _,n=model_counts()
    if n<12: raise SystemExit('negative/boundary target not met')
def parity_job():
    p=load('release/v1.4.0/GATE3_CLUSTER_B_WP4_STATEMENT_PARITY_MANIFEST.json')
    if p['coverage_percent']!=100 or any(r['parity_status']!='PASS' for r in p['records']): raise SystemExit('statement parity failure')
    proof=load('release/v1.4.0/GATE3_CLUSTER_B_WP4_DUAL_BACKEND_PROOF_MANIFEST.json')
    expected={f'T{i}' for i in range(157,163)}
    if proof['theorem_count']!=6 or {r['theorem_id'] for r in proof['theorems']}!=expected: raise SystemExit('dual-backend proof coverage failure')
    for row in proof['theorems']:
        if row['lean']['status']!='PROVED' or row['coq']['status']!='PROVED' or row['proof_holes_permitted'] or row['parity_status']!='PASS': raise SystemExit('dual-backend proof state failure '+row['theorem_id'])
def lineage_job():
    b=load('release/v1.4.0/GATE3_CLUSTER_B_WP3_ADAPTER_BINDING_MANIFEST.json')
    if b['binding_count']!=9 or len(b['bindings'])!=9: raise SystemExit('WP3 binding count failure')
    for row in b['bindings']:
        if not row['theorem_ids'] or not row['rule_ids'] or row['binding_mode']!='EXACT_WP2_RESULT_ENVELOPE': raise SystemExit('binding lineage failure '+row['case_type'])
def replay_job():
    rec=load('release/v1.4.0/GATE3_CLUSTER_B_WP5_REPLAY_RECORD.json')
    if not rec['byte_identical'] or rec['run_1_sha256']!=rec['run_2_sha256'] or rec['run_1_sha256']!=rec['canonical_bundle_sha256']: raise SystemExit('replay equivalence failure')
    for row in load('release/v1.4.0/GATE3_CLUSTER_B_WP5_FIXTURE_MANIFEST.json')['fixtures']:
        cp=run('python','scripts/replay_gate3_cluster_b_wp5.py','--fixture',row['path'],check=False)
        if cp.returncode: raise SystemExit('evidence fixture failure '+row['fixture_id']+'\n'+cp.stdout+cp.stderr)
def audit_inputs_job():
    for fn in (schemas_job,id_job,role_job,dag_job,positive_job,negative_job,parity_job,lineage_job,replay_job): fn()
    gates=load('release/v1.4.0/GATE3_CLUSTER_B_WP5_ACCEPTANCE_GATES.json')
    ids=[r['gate_id'] for r in gates['gates']]
    if gates['gate_count']!=24 or ids!=[f'WP5-G{i:02d}' for i in range(1,25)] or len(ids)!=len(set(ids)) or gates['close_gate3_authorized'] or gates['release_authorization']!='NONE': raise SystemExit('WP5 gate boundary failure')
    print('WP5 RESULT: READY_FOR_WP6_AUDIT (NO GATE3 DECISION)')
JOBS={'baseline':baseline_job,'schemas':schemas_job,'id-audit':id_job,'role-coverage':role_job,'dependency-dag':dag_job,'positive-models':positive_job,'negative-boundary':negative_job,'statement-parity':parity_job,'ipec-lineage':lineage_job,'deterministic-replay':replay_job,'gate3-audit-inputs':audit_inputs_job}
def main():
    p=argparse.ArgumentParser(); p.add_argument('--job',choices=list(JOBS)+['full'],default='full'); a=p.parse_args()
    if a.job=='full':
        baseline_job(); audit_inputs_job()
    else: JOBS[a.job]()
    print(json.dumps({'artifact':'V0_OSAP_GATE3_CLUSTER_B_WP5','job':a.job,'status':'PASS','release_authorized':False,'wp6_decision_performed':False},indent=2,sort_keys=True))
    return 0
if __name__=='__main__': raise SystemExit(main())
