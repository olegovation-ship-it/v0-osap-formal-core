#!/usr/bin/env python3
from __future__ import annotations
import hashlib, importlib.util, json, os, subprocess, sys
from pathlib import Path
from jsonschema import Draft202012Validator
ROOT=Path(__file__).resolve().parents[1]
BASELINE='7b49aa76fef65bced7141a639e8ef6fe3b5ba313'
EXACT={'.github/workflows/gate3-cluster-b-wp3.yml','checker/v0_osap_fc1/cluster_b_wp3.py','scripts/build_gate3_cluster_b_wp3.py','scripts/verify_gate3_cluster_b_wp3.py','tests/test_gate3_cluster_b_wp3.py'}
PREFIX=('docs/gate3/cluster_b/WP3_','fixtures/gate3/cluster_b/wp3/','release/v1.4.0/GATE3_CLUSTER_B_WP3_','schemas/v1.4.0/gate3_cluster_b_wp3_')
AUTHORIZED_MODIFIED={
    'scripts/verify_gate3_cluster_b_wp2.py':('af37614f25936a79cc407a28a32f0d61cd6a451023a97613a485568762af256e','ca203abbf59b60565fdc6c9333f4fb8a76de6a29ddfa8ebf19e6ee9eb65384aa'),
    'scripts/verify_gate3_cluster_b_wp2_post_merge_closeout.py':('3cece18c106c36e7abe62fd83e66f6c4c98b22ff7666c1d062ad9cf3589c253d','d4753c458e3c74462bd9cf523619788cf75c4bfc8276fd2f37216080a31c1806'),
    'release/v1.4.0/GATE3_CLUSTER_B_WP2_POST_MERGE_SHA256SUMS.txt':('f5abb673b3fd6eb8680bdd75e3dfcf7185219177cd8860c25cf9366d8c71b6d3','400d418fa006356794eea240aaf8a70af903b4af4e6f93dc6677d862e26c3447'),
}
FROZEN_PREFIX=('.github/workflows/gate3-cluster-b-wp0','.github/workflows/gate3-cluster-b-wp1','.github/workflows/gate3-cluster-b-wp2','checker/v0_osap_fc1/cluster_b_wp2.py','docs/gate3/cluster_b/WP0_','docs/gate3/cluster_b/WP1_','docs/gate3/cluster_b/WP2_','fixtures/gate3/cluster_b/wp2/','release/v1.4.0/GATE3_CLUSTER_B_WP0_','release/v1.4.0/GATE3_CLUSTER_B_WP1_','release/v1.4.0/GATE3_CLUSTER_B_WP2_','schemas/v1.4.0/gate3_cluster_b_wp0_','schemas/v1.4.0/gate3_cluster_b_wp1_','schemas/v1.4.0/gate3_cluster_b_wp2_','scripts/build_gate3_cluster_b_wp0','scripts/build_gate3_cluster_b_wp1','scripts/build_gate3_cluster_b_wp2','scripts/verify_gate3_cluster_b_wp0','scripts/verify_gate3_cluster_b_wp1','scripts/verify_gate3_cluster_b_wp2','tests/test_gate3_cluster_b_wp0','tests/test_gate3_cluster_b_wp1','tests/test_gate3_cluster_b_wp2','release/v1.4.0/tools/patch_wp2_','scripts/capture_gate3_cluster_b_wp2','scripts/synchronize_v1_4_0_development_wp2')
def run(*a,check=True,text=True): return subprocess.run(a,cwd=ROOT,capture_output=True,text=text,check=check)
def lines(*a): return [x for x in run('git',*a).stdout.splitlines() if x]
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def allowed(p): return p in AUTHORIZED_MODIFIED or p in EXACT or any(p.startswith(x) for x in PREFIX)
def verify_boundary():
    run('git','cat-file','-e',BASELINE+'^{commit}')
    head=run('git','rev-parse','HEAD').stdout.strip()
    if head!=BASELINE: run('git','merge-base','--is-ancestor',BASELINE,'HEAD')
    changed=set(lines('diff','--name-only',BASELINE,'--')); changed.update(lines('ls-files','--others','--exclude-standard'))
    bad=sorted(p for p in changed if not allowed(p))
    if bad: raise SystemExit('FAIL_PRESERVATION_FIREWALL disallowed paths: '+', '.join(bad))
    expected=set(EXACT)|set(AUTHORIZED_MODIFIED)
    expected.update(p for p in changed if any(p.startswith(x) for x in PREFIX))
    if changed!=expected:
        raise SystemExit('FAIL_PRESERVATION_FIREWALL exact delta mismatch: missing='+str(sorted(expected-changed))+', extra='+str(sorted(changed-expected)))
    status=lines('diff','--name-status',BASELINE,'--')
    for row in status:
        code,path=row.split('\t',1)
        if path in AUTHORIZED_MODIFIED:
            if code!='M': raise SystemExit('FAIL_PRESERVATION_FIREWALL authorized path must be modified: '+row)
        elif allowed(path):
            if code!='A': raise SystemExit('FAIL_PRESERVATION_FIREWALL WP3-owned path must be additive: '+row)
        else:
            raise SystemExit('FAIL_PRESERVATION_FIREWALL unexpected delta: '+row)
    for p,(pre,post) in AUTHORIZED_MODIFIED.items():
        historical=run('git','show',f'{BASELINE}:{p}',text=False).stdout
        if hashlib.sha256(historical).hexdigest()!=pre: raise SystemExit('FAIL_PRESERVATION_FIREWALL baseline hash mismatch: '+p)
        current=ROOT/p
        if not current.is_file() or digest(current)!=post: raise SystemExit('FAIL_PRESERVATION_FIREWALL replacement hash mismatch: '+p)
    for p in lines('ls-tree','-r','--name-only',BASELINE):
        if p in AUTHORIZED_MODIFIED: continue
        current=ROOT/p
        if not current.is_file(): raise SystemExit('FAIL_PRESERVATION_FIREWALL missing baseline path: '+p)
        historical=run('git','show',f'{BASELINE}:{p}',text=False).stdout
        if current.read_bytes()!=historical: raise SystemExit('FAIL_PRESERVATION_FIREWALL modified baseline path: '+p)

def verify_wp2_successor_handoff():
    env=os.environ.copy(); env['PYTHONDONTWRITEBYTECODE']='1'
    commands=[
        [sys.executable,'release/v1.4.0/tools/patch_wp2_post_merge_allowlist.py','--check'],
        [sys.executable,'scripts/build_gate3_cluster_b_wp2.py','--check'],
        [sys.executable,'scripts/build_gate3_cluster_b_wp2_post_merge_closeout.py','--check'],
        [sys.executable,'scripts/verify_gate3_cluster_b_wp2.py'],
        [sys.executable,'scripts/verify_gate3_cluster_b_wp2_post_merge_closeout.py','--package-only'],
    ]
    for cmd in commands:
        cp=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True,env=env,check=False)
        if cp.returncode: raise SystemExit('WP2 successor handoff failure: '+' '.join(cmd)+'\n'+cp.stdout+cp.stderr)

def load(rel): return json.loads((ROOT/rel).read_text(encoding='utf-8'))
def validate(obj,schema_rel):
 schema=load(schema_rel); errs=sorted(Draft202012Validator(schema).iter_errors(obj),key=lambda e:list(e.path))
 if errs: raise SystemExit(f'schema failure {schema_rel}: {errs[0].message}')
def binder():
 p=ROOT/'checker/v0_osap_fc1/cluster_b_wp3.py'; s=importlib.util.spec_from_file_location('cluster_b_wp3',p)
 if s is None or s.loader is None: raise SystemExit('cannot load binder')
 m=importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
def verify_records():
 pairs=[
 ('release/v1.4.0/GATE3_CLUSTER_B_WP3_BASELINE_LOCK.json','schemas/v1.4.0/gate3_cluster_b_wp3_baseline_lock.schema.json'),
 ('release/v1.4.0/GATE3_CLUSTER_B_WP3_IPEC_V0_1_COMPATIBILITY_PROFILE.json','schemas/v1.4.0/gate3_cluster_b_wp3_ipec_compatibility_profile.schema.json'),
 ('release/v1.4.0/GATE3_CLUSTER_B_WP3_EXTENSION_RULE_REGISTRY_T157_T162.json','schemas/v1.4.0/gate3_cluster_b_wp3_extension_rule_registry.schema.json'),
 ('release/v1.4.0/GATE3_CLUSTER_B_WP3_ADAPTER_BINDING_MANIFEST.json','schemas/v1.4.0/gate3_cluster_b_wp3_adapter_binding_manifest.schema.json'),
 ('release/v1.4.0/GATE3_CLUSTER_B_WP3_FIXTURE_MANIFEST.json','schemas/v1.4.0/gate3_cluster_b_wp3_fixture_manifest.schema.json'),
 ('release/v1.4.0/GATE3_CLUSTER_B_WP3_PRESERVATION_FIREWALL.json','schemas/v1.4.0/gate3_cluster_b_wp3_preservation_firewall.schema.json'),
 ('release/v1.4.0/GATE3_CLUSTER_B_WP3_ACCEPTANCE_GATES.json','schemas/v1.4.0/gate3_cluster_b_wp3_acceptance_gates.schema.json'),
 ('release/v1.4.0/GATE3_CLUSTER_B_WP3_SCHEMA_BUNDLE_MANIFEST.json','schemas/v1.4.0/gate3_cluster_b_wp3_schema_bundle_manifest.schema.json')]
 for r,s in pairs: validate(load(r),s)
 profile=load(pairs[1][0])
 expected=['BACKEND_PARITY_FAILURE', 'REJECTED_BRANCH_PROMOTION', 'REJECTED_NONELIM_OBSTRUCTION', 'REJECTED_LIVE_RESIDUAL', 'REJECTED_DLE_FAILURE', 'REJECTED_GUARD_FAILURE', 'INCONCLUSIVE_UNSUPPORTED_FRAGMENT', 'CERTIFIED']
 if profile['precedence']!=expected or profile['typed_outcome_records_sha256']!='4e05803bd53ecc7ed0c7926fddfb9ad517c8b14b3c795217df511a11cae60bfb': raise SystemExit('IPEC compatibility pin mismatch')
 ext=load(pairs[2][0]); tids={x['theorem_id'] for x in ext['rules']}; rids=[x['rule_id'] for x in ext['rules']]
 if tids!={'T157','T158','T159','T160','T161','T162'} or len(rids)!=len(set(rids)) or any(r.startswith('IPEC.RULE.') for r in rids): raise SystemExit('extension rule namespace/coverage failure')
def verify_fixtures():
 m=binder(); man=load('release/v1.4.0/GATE3_CLUSTER_B_WP3_FIXTURE_MANIFEST.json'); seen=set(); actual=[]
 for e in man['fixtures']:
  fx=load(e['path']); validate(fx,'schemas/v1.4.0/gate3_cluster_b_wp3_fixture.schema.json'); validate(fx['source_result'],'schemas/v1.4.0/gate3_cluster_b_wp3_source_result.schema.json')
  out=m.bind_wp2_result(fx['source_result'],fx['evidence_lineage']); validate(out,'schemas/v1.4.0/gate3_cluster_b_wp3_binding_result.schema.json')
  for k,v in fx['expected'].items():
   if out[k]!=v: raise SystemExit(f"fixture {fx['fixture_id']} mismatch {k}")
  if out['diagnostic_transport']!=fx['source_result']['diagnostics']: raise SystemExit('diagnostic transport mismatch')
  if not out['theorem_lineage'] or not out['evidence_lineage']: raise SystemExit('empty nonprocedural lineage')
  seen.add(fx['case_type']); actual.append(out['typed_outcome_code'])
 if seen!=set(m.CASE_PROFILES): raise SystemExit('case coverage incomplete')
 if 'CERTIFIED' in actual: raise SystemExit('WP3 may not claim CERTIFIED before WP4')
def main():
 verify_boundary(); verify_wp2_successor_handoff(); verify_records(); verify_fixtures()
 cp=run(sys.executable,'scripts/build_gate3_cluster_b_wp3.py','--check',check=False)
 if cp.returncode: raise SystemExit(cp.stdout+cp.stderr)
 print('WP3 VERIFICATION: PASS'); return 0
if __name__=='__main__': raise SystemExit(main())
