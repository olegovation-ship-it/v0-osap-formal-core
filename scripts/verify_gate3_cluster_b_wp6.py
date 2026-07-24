#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, os, subprocess, sys
from pathlib import Path
from jsonschema import Draft202012Validator
ROOT=Path(__file__).resolve().parents[1]
BASELINE='b3798367af960ff3b588778966c5e233d89e72ab'; BRANCH='v1.4.0-development'; TAG_TARGET='13bf095688bcabd5b090f188e9bd28a16237edeb'
EXPECTED=['.github/workflows/gate3-cluster-b-wp6.yml', 'docs/gate3/cluster_b/WP6_BUILD_SPECIFICATION.md', 'docs/gate3/cluster_b/WP6_GATE3_AUDIT_AND_RELEASE_CANDIDATE_DECISION.md', 'fixtures/gate3/cluster_b/wp6/01_all_gates_pass_close_candidate.json', 'fixtures/gate3/cluster_b/wp6/02_branch_ref_mismatch_hold.json', 'fixtures/gate3/cluster_b/wp6/03_predecessor_digest_mismatch_hold.json', 'fixtures/gate3/cluster_b/wp6/04_missing_wp5_repair_ledger_hold.json', 'fixtures/gate3/cluster_b/wp6/05_theorem_id_closure_failure_hold.json', 'fixtures/gate3/cluster_b/wp6/06_role_coverage_failure_hold.json', 'fixtures/gate3/cluster_b/wp6/07_dependency_cycle_hold.json', 'fixtures/gate3/cluster_b/wp6/08_positive_fixture_threshold_failure_hold.json', 'fixtures/gate3/cluster_b/wp6/09_negative_fixture_threshold_failure_hold.json', 'fixtures/gate3/cluster_b/wp6/10_typed_lineage_gap_hold.json', 'fixtures/gate3/cluster_b/wp6/11_backend_or_parity_failure_hold.json', 'fixtures/gate3/cluster_b/wp6/12_replay_nondeterminism_hold.json', 'fixtures/gate3/cluster_b/wp6/13_claim_perimeter_expansion_hold.json', 'fixtures/gate3/cluster_b/wp6/14_release_or_close_authorization_injection_rejected.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP6_ACCEPTANCE_GATES.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP6_BASELINE_LOCK.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP6_BLOCKER_REGISTER.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP6_BUILD_PLAN.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP6_CI_JOB_MATRIX.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP6_CLAIM_PERIMETER.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP6_DECISION_CANDIDATE.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP6_EVIDENCE_INPUT_MANIFEST.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP6_FIXTURE_MANIFEST.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP6_GATE_RESULT_MATRIX.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP6_PRESERVATION_FIREWALL.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP6_REPLAY_RECORD.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP6_SCHEMA_BUNDLE_MANIFEST.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP6_SHA256SUMS.txt', 'release/v1.4.0/tools/patch_wp6_allowlist.py', 'release/v1.4.0/tools/patch_wp6_build_spec_allowlist.py', 'schemas/v1.4.0/gate3_cluster_b_wp6_acceptance_gates.schema.json', 'schemas/v1.4.0/gate3_cluster_b_wp6_audit_fixture.schema.json', 'schemas/v1.4.0/gate3_cluster_b_wp6_baseline_lock.schema.json', 'schemas/v1.4.0/gate3_cluster_b_wp6_blocker_register.schema.json', 'schemas/v1.4.0/gate3_cluster_b_wp6_build_plan.schema.json', 'schemas/v1.4.0/gate3_cluster_b_wp6_ci_job_matrix.schema.json', 'schemas/v1.4.0/gate3_cluster_b_wp6_claim_perimeter.schema.json', 'schemas/v1.4.0/gate3_cluster_b_wp6_decision_candidate.schema.json', 'schemas/v1.4.0/gate3_cluster_b_wp6_evidence_input_manifest.schema.json', 'schemas/v1.4.0/gate3_cluster_b_wp6_fixture_manifest.schema.json', 'schemas/v1.4.0/gate3_cluster_b_wp6_gate_result_matrix.schema.json', 'schemas/v1.4.0/gate3_cluster_b_wp6_preservation_firewall.schema.json', 'schemas/v1.4.0/gate3_cluster_b_wp6_replay_record.schema.json', 'schemas/v1.4.0/gate3_cluster_b_wp6_schema_bundle_manifest.schema.json', 'scripts/build_gate3_cluster_b_wp6.py', 'scripts/capture_gate3_cluster_b_wp6_audit_evidence.py', 'scripts/replay_gate3_cluster_b_wp6.py', 'scripts/verify_gate3_cluster_b_wp6.py', 'scripts/verify_gate3_cluster_b_wp6_build_spec.py', 'tests/test_gate3_cluster_b_wp6.py', 'tests/test_gate3_cluster_b_wp6_build_spec.py']; EVIDENCE=['docs/gate3/cluster_b/BASELINE_AUDIT_AND_BUILD_SPECIFICATION_v0.1.md', 'release/v1.4.0/GATE3_CLUSTER_B_WP0_POST_MERGE_SHA256SUMS.txt', 'release/v1.4.0/GATE3_CLUSTER_B_WP0_SCHEMA_BUNDLE_MANIFEST.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP1_DEPENDENCY_DAG.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP1_POST_MERGE_SHA256SUMS.txt', 'release/v1.4.0/GATE3_CLUSTER_B_WP1_SEMANTIC_ROLE_MAP.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP1_THEOREM_REGISTRY_T157_T162.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP2_FIXTURE_MANIFEST.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP2_POST_MERGE_SHA256SUMS.txt', 'release/v1.4.0/GATE3_CLUSTER_B_WP2_SEMANTICS_PROFILE.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP3_ADAPTER_BINDING_MANIFEST.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP3_EXTENSION_RULE_REGISTRY_T157_T162.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP3_POST_MERGE_SHA256SUMS.txt', 'release/v1.4.0/GATE3_CLUSTER_B_WP4_DUAL_BACKEND_PROOF_MANIFEST.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP4_FIXTURE_MANIFEST.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP4_POST_MERGE_FROZEN_UPSTREAM_PRESERVATION_RECORD.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP4_POST_MERGE_SHA256SUMS.txt', 'release/v1.4.0/GATE3_CLUSTER_B_WP4_STATEMENT_PARITY_MANIFEST.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP5_ACCEPTANCE_GATES.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP5_BASELINE_LOCK.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP5_CI_JOB_MATRIX.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP5_DEVELOPMENT_BRANCH_SYNCHRONIZATION_RECORD.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP5_EVIDENCE_INPUT_MANIFEST.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP5_FIXTURE_MANIFEST.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP5_POST_MERGE_ARCHIVAL_CLOSEOUT_RECORD.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP5_POST_MERGE_CLOSEOUT_GATES.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP5_POST_MERGE_FROZEN_UPSTREAM_PRESERVATION_RECORD.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP5_POST_MERGE_HOSTED_CI_EVIDENCE.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP5_POST_MERGE_SCHEMA_BUNDLE_MANIFEST.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP5_POST_MERGE_SHA256SUMS.txt', 'release/v1.4.0/GATE3_CLUSTER_B_WP5_PRESERVATION_FIREWALL.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP5_REPLAY_RECORD.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP5_SCHEMA_BUNDLE_MANIFEST.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP5_SHA256SUMS.txt', 'release/v1.4.0/GATE3_CLUSTER_B_WP5_SYNC_HELPER_REPAIR_ACCEPTANCE_GATES.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP5_SYNC_HELPER_REPAIR_FIXTURE_MANIFEST.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP5_SYNC_HELPER_REPAIR_RECORD.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP5_SYNC_HELPER_REPAIR_SCHEMA_BUNDLE_MANIFEST.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP5_SYNC_HELPER_REPAIR_SHA256SUMS.txt']
SCHEMA_MAP={
'release/v1.4.0/GATE3_CLUSTER_B_WP6_ACCEPTANCE_GATES.json':'schemas/v1.4.0/gate3_cluster_b_wp6_acceptance_gates.schema.json',
'release/v1.4.0/GATE3_CLUSTER_B_WP6_BASELINE_LOCK.json':'schemas/v1.4.0/gate3_cluster_b_wp6_baseline_lock.schema.json',
'release/v1.4.0/GATE3_CLUSTER_B_WP6_BLOCKER_REGISTER.json':'schemas/v1.4.0/gate3_cluster_b_wp6_blocker_register.schema.json',
'release/v1.4.0/GATE3_CLUSTER_B_WP6_BUILD_PLAN.json':'schemas/v1.4.0/gate3_cluster_b_wp6_build_plan.schema.json',
'release/v1.4.0/GATE3_CLUSTER_B_WP6_CI_JOB_MATRIX.json':'schemas/v1.4.0/gate3_cluster_b_wp6_ci_job_matrix.schema.json',
'release/v1.4.0/GATE3_CLUSTER_B_WP6_CLAIM_PERIMETER.json':'schemas/v1.4.0/gate3_cluster_b_wp6_claim_perimeter.schema.json',
'release/v1.4.0/GATE3_CLUSTER_B_WP6_DECISION_CANDIDATE.json':'schemas/v1.4.0/gate3_cluster_b_wp6_decision_candidate.schema.json',
'release/v1.4.0/GATE3_CLUSTER_B_WP6_EVIDENCE_INPUT_MANIFEST.json':'schemas/v1.4.0/gate3_cluster_b_wp6_evidence_input_manifest.schema.json',
'release/v1.4.0/GATE3_CLUSTER_B_WP6_FIXTURE_MANIFEST.json':'schemas/v1.4.0/gate3_cluster_b_wp6_fixture_manifest.schema.json',
'release/v1.4.0/GATE3_CLUSTER_B_WP6_GATE_RESULT_MATRIX.json':'schemas/v1.4.0/gate3_cluster_b_wp6_gate_result_matrix.schema.json',
'release/v1.4.0/GATE3_CLUSTER_B_WP6_PRESERVATION_FIREWALL.json':'schemas/v1.4.0/gate3_cluster_b_wp6_preservation_firewall.schema.json',
'release/v1.4.0/GATE3_CLUSTER_B_WP6_REPLAY_RECORD.json':'schemas/v1.4.0/gate3_cluster_b_wp6_replay_record.schema.json',
'release/v1.4.0/GATE3_CLUSTER_B_WP6_SCHEMA_BUNDLE_MANIFEST.json':'schemas/v1.4.0/gate3_cluster_b_wp6_schema_bundle_manifest.schema.json'}
def load(p): return json.loads((ROOT/p).read_text())
def digest(p): return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def run(*a,check=True,cwd=None):
 cp=subprocess.run(a,cwd=cwd or ROOT,capture_output=True,text=True,check=False)
 if check and cp.returncode: raise SystemExit(cp.stdout+cp.stderr)
 return cp
def schemas():
 for data,schema in SCHEMA_MAP.items():
  errs=sorted(Draft202012Validator(load(schema)).iter_errors(load(data)),key=lambda e:list(e.path))
  if errs: raise SystemExit(data+': '+errs[0].message)
 fs='schemas/v1.4.0/gate3_cluster_b_wp6_audit_fixture.schema.json'
 for p in [x for x in EXPECTED if x.startswith('fixtures/gate3/cluster_b/wp6/')]:
  errs=list(Draft202012Validator(load(fs)).iter_errors(load(p)))
  if errs: raise SystemExit(p+': '+errs[0].message)
def baseline():
 b=load('release/v1.4.0/GATE3_CLUSTER_B_WP6_BASELINE_LOCK.json')
 if b['baseline_commit']!=BASELINE or b['stable_tag_target']!=TAG_TARGET: raise SystemExit('baseline-lock record mismatch')
 head=run('git','rev-parse','HEAD').stdout.strip()
 if run('git','merge-base','--is-ancestor',BASELINE,head,check=False).returncode: raise SystemExit('baseline is not ancestor')
 if os.environ.get('GITHUB_ACTIONS')!='true':
  if head!=BASELINE: raise SystemExit('local WP6 implementation must remain uncommitted on exact baseline')
  if run('git','branch','--show-current').stdout.strip()!=BRANCH: raise SystemExit('branch mismatch')
  for ref in ('origin/main','origin/'+BRANCH):
   if run('git','rev-parse',ref).stdout.strip()!=BASELINE: raise SystemExit(ref+' mismatch')
 if run('git','rev-parse','refs/tags/v1.3.0^{}').stdout.strip()!=TAG_TARGET: raise SystemExit('tag target changed')
 run(sys.executable,'release/v1.4.0/tools/patch_wp6_allowlist.py')
def predecessor():
 m=load('release/v1.4.0/GATE3_CLUSTER_B_WP6_EVIDENCE_INPUT_MANIFEST.json')
 if m['entry_count']!=len(EVIDENCE) or [x['path'] for x in m['entries']]!=EVIDENCE: raise SystemExit('evidence path inventory mismatch')
 for x in m['entries']:
  if not (ROOT/x['path']).is_file() or digest(x['path'])!=x['sha256']: raise SystemExit('predecessor digest mismatch: '+x['path'])
def theorem_role_dag():
 reg=load('release/v1.4.0/GATE3_CLUSTER_B_WP1_THEOREM_REGISTRY_T157_T162.json')
 ids=[x['theorem_id'] for x in reg['records']]
 if ids!=[f'T{i}' for i in range(157,163)]: raise SystemExit('T157-T162 identity closure failure')
 rm=load('release/v1.4.0/GATE3_CLUSTER_B_WP1_SEMANTIC_ROLE_MAP.json')
 if rm.get('required_role_count')!=7 or {x['role_id'] for x in rm['roles']}!={f'CB-R{i}' for i in range(1,8)}: raise SystemExit('role coverage failure')
 dag=load('release/v1.4.0/GATE3_CLUSTER_B_WP1_DEPENDENCY_DAG.json')
 nodes={x['theorem_id']:x.get('requires',[]) for x in dag['nodes']}
 if dag.get('cluster_node_count')!=16 or len(nodes)!=16: raise SystemExit('DAG node count failure')
 temp=set(); done=set()
 def visit(n):
  if n in temp: raise SystemExit('DAG cycle')
  if n in done: return
  temp.add(n)
  for q in nodes.get(n,[]):
   if q in nodes: visit(q)
  temp.remove(n); done.add(n)
 for n in nodes: visit(n)
def semantic():
 m=load('release/v1.4.0/GATE3_CLUSTER_B_WP2_FIXTURE_MANIFEST.json'); rows=m['fixtures']
 pos=sum(x.get('status')=='PASS' for x in rows); neg=sum(x.get('status')!='PASS' for x in rows)
 if pos<12 or neg<12 or m.get('fixture_count',len(rows))<24: raise SystemExit(f'WP2 threshold failure pos={pos} neg={neg}')
 if not any(x.get('case_type')=='MODEL_PAIR_NONELIMINABILITY' and x.get('status')=='PASS' for x in rows): raise SystemExit('model-pair evidence missing')
def lineage():
 m=load('release/v1.4.0/GATE3_CLUSTER_B_WP3_ADAPTER_BINDING_MANIFEST.json')
 if m.get('binding_count')!=9 or len(m.get('bindings',[]))!=9: raise SystemExit('WP3 binding count failure')
 for b in m['bindings']:
  if not b.get('theorem_ids') or not b.get('rule_ids') or not b.get('role_ids'): raise SystemExit('typed lineage gap')
def proof_parity():
 m=load('release/v1.4.0/GATE3_CLUSTER_B_WP4_DUAL_BACKEND_PROOF_MANIFEST.json')
 if m.get('theorem_count')!=6: raise SystemExit('proof count failure')
 for t in m['theorems']:
  if t['lean']['status']!='PROVED' or t['coq']['status']!='PROVED' or t.get('parity_status')!='PASS' or t.get('proof_holes_permitted'): raise SystemExit('dual-backend proof failure')
 p=load('release/v1.4.0/GATE3_CLUSTER_B_WP4_STATEMENT_PARITY_MANIFEST.json')
 text=json.dumps(p)
 if 'PASS' not in text or any(x not in text for x in [f'T{i}' for i in range(157,163)]): raise SystemExit('statement parity failure')
def integrity():
 fm=load('release/v1.4.0/GATE3_CLUSTER_B_WP6_FIXTURE_MANIFEST.json')
 if fm['fixture_count']!=14: raise SystemExit('fixture count')
 for x in fm['fixtures']:
  if digest(x['path'])!=x['sha256']: raise SystemExit('fixture digest')
 sm=load('release/v1.4.0/GATE3_CLUSTER_B_WP6_SCHEMA_BUNDLE_MANIFEST.json')
 if sm['schema_count']!=14: raise SystemExit('schema count')
 for x in sm['schemas']:
  if digest(x['path'])!=x['sha256']: raise SystemExit('schema digest')
 expected={}
 for line in (ROOT/'release/v1.4.0/GATE3_CLUSTER_B_WP6_SHA256SUMS.txt').read_text().splitlines():
  if line.strip(): h,p=line.split('  ',1); expected[p]=h
 for p,h in expected.items():
  if digest(p)!=h: raise SystemExit('WP6 ledger mismatch: '+p)
def replay_claims():
 r=load('release/v1.4.0/GATE3_CLUSTER_B_WP6_REPLAY_RECORD.json')
 if not r['byte_identical'] or r['run_1_sha256']!=r['run_2_sha256']: raise SystemExit('replay failure')
 c=load('release/v1.4.0/GATE3_CLUSTER_B_WP6_CLAIM_PERIMETER.json')
 if c['new_numbered_theorems']: raise SystemExit('new theorem introduced')
def fixtures():
 for p in [x for x in EXPECTED if x.startswith('fixtures/gate3/cluster_b/wp6/')]:
  f=load(p)
  if f['fixture_id']=='14':
   if f['valid_input'] or f['expected_disposition']!='REJECT_UNAUTHORIZED_INPUT': raise SystemExit('fixture 14 authorization firewall failure')
  elif f['fixture_id']=='01':
   if f['expected_disposition']!='ELIGIBLE_FOR_CLOSE_GATE3_PENDING_EXPLICIT_AUTHORIZATION': raise SystemExit('fixture 01 failure')
  elif f['expected_disposition']!='HOLD_WITH_EXPLICIT_BLOCKERS' or not f['expected_blockers']: raise SystemExit('negative audit fixture failure')
def decision():
 a=load('release/v1.4.0/GATE3_CLUSTER_B_WP6_ACCEPTANCE_GATES.json'); g=load('release/v1.4.0/GATE3_CLUSTER_B_WP6_GATE_RESULT_MATRIX.json'); d=load('release/v1.4.0/GATE3_CLUSTER_B_WP6_DECISION_CANDIDATE.json'); b=load('release/v1.4.0/GATE3_CLUSTER_B_WP6_BLOCKER_REGISTER.json')
 if a['gate_count']!=24 or any(x['status']!='PASS' for x in a['gates']): raise SystemExit('acceptance gate failure')
 if not g['all_mandatory_local_gates_pass'] or d['candidate']!='HOLD_WITH_EXPLICIT_BLOCKERS' or d['gate3_closed'] or d['release_authorized']: raise SystemExit('decision firewall failure')
 if b['blocker_count']<1 or not any(x['status']=='OPEN' and x['blocks_canonical_gate3_close'] for x in b['blockers']): raise SystemExit('blocker register failure')
def full():
 schemas(); predecessor(); theorem_role_dag(); semantic(); lineage(); proof_parity(); integrity(); replay_claims(); fixtures(); decision(); baseline()
if __name__=='__main__':
 ap=argparse.ArgumentParser(); ap.add_argument('--job',default='full',choices=['full','baseline-lock','predecessor-chain','theorem-role-dag','semantic-evidence','typed-lineage','schemas-fixtures-python','lean-proof-holes','coq-parity','replay-claims','decision-firewall']); a=ap.parse_args()
 jobs={'full':full,'baseline-lock':baseline,'predecessor-chain':predecessor,'theorem-role-dag':theorem_role_dag,'semantic-evidence':semantic,'typed-lineage':lineage,'schemas-fixtures-python':lambda:(schemas(),integrity(),fixtures()),'lean-proof-holes':proof_parity,'coq-parity':proof_parity,'replay-claims':lambda:(replay_claims(),integrity()),'decision-firewall':lambda:(decision(),baseline())}
 jobs[a.job](); print('WP6 VERIFIER: PASS ['+a.job+']')
