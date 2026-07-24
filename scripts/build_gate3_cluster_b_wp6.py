#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BASELINE='b3798367af960ff3b588778966c5e233d89e72ab'
EVIDENCE=['docs/gate3/cluster_b/BASELINE_AUDIT_AND_BUILD_SPECIFICATION_v0.1.md', 'release/v1.4.0/GATE3_CLUSTER_B_WP0_POST_MERGE_SHA256SUMS.txt', 'release/v1.4.0/GATE3_CLUSTER_B_WP0_SCHEMA_BUNDLE_MANIFEST.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP1_DEPENDENCY_DAG.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP1_POST_MERGE_SHA256SUMS.txt', 'release/v1.4.0/GATE3_CLUSTER_B_WP1_SEMANTIC_ROLE_MAP.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP1_THEOREM_REGISTRY_T157_T162.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP2_FIXTURE_MANIFEST.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP2_POST_MERGE_SHA256SUMS.txt', 'release/v1.4.0/GATE3_CLUSTER_B_WP2_SEMANTICS_PROFILE.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP3_ADAPTER_BINDING_MANIFEST.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP3_EXTENSION_RULE_REGISTRY_T157_T162.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP3_POST_MERGE_SHA256SUMS.txt', 'release/v1.4.0/GATE3_CLUSTER_B_WP4_DUAL_BACKEND_PROOF_MANIFEST.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP4_FIXTURE_MANIFEST.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP4_POST_MERGE_FROZEN_UPSTREAM_PRESERVATION_RECORD.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP4_POST_MERGE_SHA256SUMS.txt', 'release/v1.4.0/GATE3_CLUSTER_B_WP4_STATEMENT_PARITY_MANIFEST.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP5_ACCEPTANCE_GATES.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP5_BASELINE_LOCK.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP5_CI_JOB_MATRIX.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP5_DEVELOPMENT_BRANCH_SYNCHRONIZATION_RECORD.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP5_EVIDENCE_INPUT_MANIFEST.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP5_FIXTURE_MANIFEST.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP5_POST_MERGE_ARCHIVAL_CLOSEOUT_RECORD.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP5_POST_MERGE_CLOSEOUT_GATES.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP5_POST_MERGE_FROZEN_UPSTREAM_PRESERVATION_RECORD.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP5_POST_MERGE_HOSTED_CI_EVIDENCE.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP5_POST_MERGE_SCHEMA_BUNDLE_MANIFEST.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP5_POST_MERGE_SHA256SUMS.txt', 'release/v1.4.0/GATE3_CLUSTER_B_WP5_PRESERVATION_FIREWALL.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP5_REPLAY_RECORD.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP5_SCHEMA_BUNDLE_MANIFEST.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP5_SHA256SUMS.txt', 'release/v1.4.0/GATE3_CLUSTER_B_WP5_SYNC_HELPER_REPAIR_ACCEPTANCE_GATES.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP5_SYNC_HELPER_REPAIR_FIXTURE_MANIFEST.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP5_SYNC_HELPER_REPAIR_RECORD.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP5_SYNC_HELPER_REPAIR_SCHEMA_BUNDLE_MANIFEST.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP5_SYNC_HELPER_REPAIR_SHA256SUMS.txt']
EXPECTED=['.github/workflows/gate3-cluster-b-wp6.yml', 'docs/gate3/cluster_b/WP6_BUILD_SPECIFICATION.md', 'docs/gate3/cluster_b/WP6_GATE3_AUDIT_AND_RELEASE_CANDIDATE_DECISION.md', 'fixtures/gate3/cluster_b/wp6/01_all_gates_pass_close_candidate.json', 'fixtures/gate3/cluster_b/wp6/02_branch_ref_mismatch_hold.json', 'fixtures/gate3/cluster_b/wp6/03_predecessor_digest_mismatch_hold.json', 'fixtures/gate3/cluster_b/wp6/04_missing_wp5_repair_ledger_hold.json', 'fixtures/gate3/cluster_b/wp6/05_theorem_id_closure_failure_hold.json', 'fixtures/gate3/cluster_b/wp6/06_role_coverage_failure_hold.json', 'fixtures/gate3/cluster_b/wp6/07_dependency_cycle_hold.json', 'fixtures/gate3/cluster_b/wp6/08_positive_fixture_threshold_failure_hold.json', 'fixtures/gate3/cluster_b/wp6/09_negative_fixture_threshold_failure_hold.json', 'fixtures/gate3/cluster_b/wp6/10_typed_lineage_gap_hold.json', 'fixtures/gate3/cluster_b/wp6/11_backend_or_parity_failure_hold.json', 'fixtures/gate3/cluster_b/wp6/12_replay_nondeterminism_hold.json', 'fixtures/gate3/cluster_b/wp6/13_claim_perimeter_expansion_hold.json', 'fixtures/gate3/cluster_b/wp6/14_release_or_close_authorization_injection_rejected.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP6_ACCEPTANCE_GATES.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP6_BASELINE_LOCK.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP6_BLOCKER_REGISTER.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP6_BUILD_PLAN.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP6_CI_JOB_MATRIX.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP6_CLAIM_PERIMETER.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP6_DECISION_CANDIDATE.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP6_EVIDENCE_INPUT_MANIFEST.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP6_FIXTURE_MANIFEST.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP6_GATE_RESULT_MATRIX.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP6_PRESERVATION_FIREWALL.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP6_REPLAY_RECORD.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP6_SCHEMA_BUNDLE_MANIFEST.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP6_SHA256SUMS.txt', 'release/v1.4.0/tools/patch_wp6_allowlist.py', 'release/v1.4.0/tools/patch_wp6_build_spec_allowlist.py', 'schemas/v1.4.0/gate3_cluster_b_wp6_acceptance_gates.schema.json', 'schemas/v1.4.0/gate3_cluster_b_wp6_audit_fixture.schema.json', 'schemas/v1.4.0/gate3_cluster_b_wp6_baseline_lock.schema.json', 'schemas/v1.4.0/gate3_cluster_b_wp6_blocker_register.schema.json', 'schemas/v1.4.0/gate3_cluster_b_wp6_build_plan.schema.json', 'schemas/v1.4.0/gate3_cluster_b_wp6_ci_job_matrix.schema.json', 'schemas/v1.4.0/gate3_cluster_b_wp6_claim_perimeter.schema.json', 'schemas/v1.4.0/gate3_cluster_b_wp6_decision_candidate.schema.json', 'schemas/v1.4.0/gate3_cluster_b_wp6_evidence_input_manifest.schema.json', 'schemas/v1.4.0/gate3_cluster_b_wp6_fixture_manifest.schema.json', 'schemas/v1.4.0/gate3_cluster_b_wp6_gate_result_matrix.schema.json', 'schemas/v1.4.0/gate3_cluster_b_wp6_preservation_firewall.schema.json', 'schemas/v1.4.0/gate3_cluster_b_wp6_replay_record.schema.json', 'schemas/v1.4.0/gate3_cluster_b_wp6_schema_bundle_manifest.schema.json', 'scripts/build_gate3_cluster_b_wp6.py', 'scripts/capture_gate3_cluster_b_wp6_audit_evidence.py', 'scripts/replay_gate3_cluster_b_wp6.py', 'scripts/verify_gate3_cluster_b_wp6.py', 'scripts/verify_gate3_cluster_b_wp6_build_spec.py', 'tests/test_gate3_cluster_b_wp6.py', 'tests/test_gate3_cluster_b_wp6_build_spec.py']
SCHEMAS=[p for p in EXPECTED if p.startswith('schemas/v1.4.0/gate3_cluster_b_wp6_')]
FIXTURES=[p for p in EXPECTED if p.startswith('fixtures/gate3/cluster_b/wp6/')]
DYNAMIC=[
'release/v1.4.0/GATE3_CLUSTER_B_WP6_EVIDENCE_INPUT_MANIFEST.json',
'release/v1.4.0/GATE3_CLUSTER_B_WP6_FIXTURE_MANIFEST.json',
'release/v1.4.0/GATE3_CLUSTER_B_WP6_REPLAY_RECORD.json',
'release/v1.4.0/GATE3_CLUSTER_B_WP6_SCHEMA_BUNDLE_MANIFEST.json',
'release/v1.4.0/GATE3_CLUSTER_B_WP6_SHA256SUMS.txt']

def digest(p:Path)->str: return hashlib.sha256(p.read_bytes()).hexdigest()
def enc(o)->bytes: return (json.dumps(o,sort_keys=True,indent=2,ensure_ascii=False)+'\n').encode()
def put(rel:str,data:bytes,check:bool):
 p=ROOT/rel
 if check:
  if not p.is_file() or p.read_bytes()!=data: raise SystemExit('WP6 deterministic build mismatch: '+rel)
 else:
  p.parent.mkdir(parents=True,exist_ok=True); p.write_bytes(data)
def build(check:bool=False):
 missing=[p for p in EVIDENCE if not (ROOT/p).is_file()]
 if missing: raise SystemExit('WP6 evidence input missing: '+repr(missing))
 entries=[{'path':p,'sha256':digest(ROOT/p)} for p in EVIDENCE]
 evidence={'artifact_id':'V0_OSAP_GATE3_CLUSTER_B_WP6_EVIDENCE_INPUT_MANIFEST','version':'0.1','baseline_commit':BASELINE,'entry_count':len(entries),'entries':entries,'serialization_profile':'SORTED_UTF8_JSON'}
 put(DYNAMIC[0],enc(evidence),check)
 fixtures=[]
 for p in FIXTURES:
  obj=json.loads((ROOT/p).read_text()); fixtures.append({'fixture_id':obj['fixture_id'],'path':p,'sha256':digest(ROOT/p),'expected_disposition':obj['expected_disposition']})
 fm={'artifact_id':'V0_OSAP_GATE3_CLUSTER_B_WP6_FIXTURE_MANIFEST','version':'0.1','fixture_count':len(fixtures),'fixtures':fixtures}
 put(DYNAMIC[1],enc(fm),check)
 schemas=[{'path':p,'sha256':digest(ROOT/p)} for p in SCHEMAS]
 sm={'artifact_id':'V0_OSAP_GATE3_CLUSTER_B_WP6_SCHEMA_BUNDLE_MANIFEST','version':'0.1','schema_count':len(schemas),'schemas':schemas}
 put(DYNAMIC[3],enc(sm),check)
 bundle_paths=[p for p in EXPECTED if p.startswith('release/v1.4.0/GATE3_CLUSTER_B_WP6_') and p not in (DYNAMIC[2],DYNAMIC[4])]
 blob=b''.join((p+'\n').encode()+ (ROOT/p).read_bytes() for p in sorted(bundle_paths))
 h=hashlib.sha256(blob).hexdigest()
 replay={'artifact_id':'V0_OSAP_GATE3_CLUSTER_B_WP6_REPLAY_RECORD','version':'0.1','run_count':2,'run_1_sha256':h,'run_2_sha256':h,'byte_identical':True,'canonical_bundle_path_count':len(bundle_paths),'serialization_profile':'V0_OSAP_CJ_1_SORTED_UTF8_COMPACT'}
 put(DYNAMIC[2],enc(replay),check)
 ledger=''.join(f"{digest(ROOT/p)}  {p}\n" for p in sorted(EXPECTED) if p!=DYNAMIC[4]).encode()
 put(DYNAMIC[4],ledger,check)
 print('WP6 DETERMINISTIC BUILD: PASS'+(' (check)' if check else ''))
if __name__=='__main__':
 ap=argparse.ArgumentParser(); ap.add_argument('--check',action='store_true'); a=ap.parse_args(); build(a.check)
