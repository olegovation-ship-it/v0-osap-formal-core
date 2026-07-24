#!/usr/bin/env python3
from __future__ import annotations
import subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
BASELINE='b3798367af960ff3b588778966c5e233d89e72ab'
TAG_TARGET='13bf095688bcabd5b090f188e9bd28a16237edeb'
EXPECTED=['.github/workflows/gate3-cluster-b-wp6.yml', 'docs/gate3/cluster_b/WP6_BUILD_SPECIFICATION.md', 'docs/gate3/cluster_b/WP6_GATE3_AUDIT_AND_RELEASE_CANDIDATE_DECISION.md', 'fixtures/gate3/cluster_b/wp6/01_all_gates_pass_close_candidate.json', 'fixtures/gate3/cluster_b/wp6/02_branch_ref_mismatch_hold.json', 'fixtures/gate3/cluster_b/wp6/03_predecessor_digest_mismatch_hold.json', 'fixtures/gate3/cluster_b/wp6/04_missing_wp5_repair_ledger_hold.json', 'fixtures/gate3/cluster_b/wp6/05_theorem_id_closure_failure_hold.json', 'fixtures/gate3/cluster_b/wp6/06_role_coverage_failure_hold.json', 'fixtures/gate3/cluster_b/wp6/07_dependency_cycle_hold.json', 'fixtures/gate3/cluster_b/wp6/08_positive_fixture_threshold_failure_hold.json', 'fixtures/gate3/cluster_b/wp6/09_negative_fixture_threshold_failure_hold.json', 'fixtures/gate3/cluster_b/wp6/10_typed_lineage_gap_hold.json', 'fixtures/gate3/cluster_b/wp6/11_backend_or_parity_failure_hold.json', 'fixtures/gate3/cluster_b/wp6/12_replay_nondeterminism_hold.json', 'fixtures/gate3/cluster_b/wp6/13_claim_perimeter_expansion_hold.json', 'fixtures/gate3/cluster_b/wp6/14_release_or_close_authorization_injection_rejected.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP6_ACCEPTANCE_GATES.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP6_BASELINE_LOCK.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP6_BLOCKER_REGISTER.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP6_BUILD_PLAN.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP6_CI_JOB_MATRIX.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP6_CLAIM_PERIMETER.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP6_DECISION_CANDIDATE.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP6_EVIDENCE_INPUT_MANIFEST.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP6_FIXTURE_MANIFEST.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP6_GATE_RESULT_MATRIX.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP6_PRESERVATION_FIREWALL.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP6_REPLAY_RECORD.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP6_SCHEMA_BUNDLE_MANIFEST.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP6_SHA256SUMS.txt', 'release/v1.4.0/tools/patch_wp6_allowlist.py', 'release/v1.4.0/tools/patch_wp6_build_spec_allowlist.py', 'schemas/v1.4.0/gate3_cluster_b_wp6_acceptance_gates.schema.json', 'schemas/v1.4.0/gate3_cluster_b_wp6_audit_fixture.schema.json', 'schemas/v1.4.0/gate3_cluster_b_wp6_baseline_lock.schema.json', 'schemas/v1.4.0/gate3_cluster_b_wp6_blocker_register.schema.json', 'schemas/v1.4.0/gate3_cluster_b_wp6_build_plan.schema.json', 'schemas/v1.4.0/gate3_cluster_b_wp6_ci_job_matrix.schema.json', 'schemas/v1.4.0/gate3_cluster_b_wp6_claim_perimeter.schema.json', 'schemas/v1.4.0/gate3_cluster_b_wp6_decision_candidate.schema.json', 'schemas/v1.4.0/gate3_cluster_b_wp6_evidence_input_manifest.schema.json', 'schemas/v1.4.0/gate3_cluster_b_wp6_fixture_manifest.schema.json', 'schemas/v1.4.0/gate3_cluster_b_wp6_gate_result_matrix.schema.json', 'schemas/v1.4.0/gate3_cluster_b_wp6_preservation_firewall.schema.json', 'schemas/v1.4.0/gate3_cluster_b_wp6_replay_record.schema.json', 'schemas/v1.4.0/gate3_cluster_b_wp6_schema_bundle_manifest.schema.json', 'scripts/build_gate3_cluster_b_wp6.py', 'scripts/capture_gate3_cluster_b_wp6_audit_evidence.py', 'scripts/replay_gate3_cluster_b_wp6.py', 'scripts/verify_gate3_cluster_b_wp6.py', 'scripts/verify_gate3_cluster_b_wp6_build_spec.py', 'tests/test_gate3_cluster_b_wp6.py', 'tests/test_gate3_cluster_b_wp6_build_spec.py']
FORBIDDEN=('checker/','lean/','coq/','fixtures/gate3/cluster_b/wp0','fixtures/gate3/cluster_b/wp1','fixtures/gate3/cluster_b/wp2','fixtures/gate3/cluster_b/wp3','fixtures/gate3/cluster_b/wp4','fixtures/gate3/cluster_b/wp5','release/v1.4.0/GATE3_CLUSTER_B_WP0_','release/v1.4.0/GATE3_CLUSTER_B_WP1_','release/v1.4.0/GATE3_CLUSTER_B_WP2_','release/v1.4.0/GATE3_CLUSTER_B_WP3_','release/v1.4.0/GATE3_CLUSTER_B_WP4_','release/v1.4.0/GATE3_CLUSTER_B_WP5_')
def run(*a,check=True):
 cp=subprocess.run(a,cwd=ROOT,capture_output=True,text=True,check=False)
 if check and cp.returncode: raise SystemExit(cp.stdout+cp.stderr)
 return cp
def lines(*a): return [x for x in run('git',*a).stdout.splitlines() if x]
if __name__=='__main__':
 run('git','cat-file','-e',BASELINE+'^{commit}')
 if run('git','merge-base','--is-ancestor',BASELINE,'HEAD',check=False).returncode: raise SystemExit('WP6 baseline is not an ancestor of HEAD')
 changed=set(lines('diff','--name-only',BASELINE,'--')); changed.update(lines('ls-files','--others','--exclude-standard'))
 exp=set(EXPECTED)
 if changed!=exp: raise SystemExit('WP6 ALLOWLIST mismatch missing='+repr(sorted(exp-changed))+' extra='+repr(sorted(changed-exp)))
 if any(p.startswith(FORBIDDEN) for p in changed): raise SystemExit('frozen predecessor path changed')
 statuses={}
 for row in lines('diff','--name-status',BASELINE,'--'):
  parts=row.split('\t'); statuses[parts[-1]]=parts[0]
 for p in lines('ls-files','--others','--exclude-standard'): statuses[p]='A'
 if any(statuses.get(p)!='A' for p in EXPECTED): raise SystemExit('all WP6 paths must be additive')
 if run('git','rev-parse','refs/tags/v1.3.0^{}').stdout.strip()!=TAG_TARGET: raise SystemExit('stable tag target changed')
 print('WP6 EXACT 54-PATH ADDITIVE ALLOWLIST: PASS')
