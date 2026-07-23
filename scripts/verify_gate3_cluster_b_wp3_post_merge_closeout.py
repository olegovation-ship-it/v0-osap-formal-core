#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, os, subprocess
from pathlib import Path
from jsonschema import Draft202012Validator
ROOT=Path(__file__).resolve().parents[1]
MERGE='3a3100d88772f3613192db200918d392885a3961'; ACCEPTED='380b5a59dd9e68ad3c67e26c01ac01bdc9e11cfe'; DEV='v1.4.0-development'; TAG_TARGET='13bf095688bcabd5b090f188e9bd28a16237edeb'
HISTORICAL=ROOT/'release/v1.4.0/GATE3_CLUSTER_B_WP3_SHA256SUMS.txt'
SUCCESSOR=ROOT/'release/v1.4.0/GATE3_CLUSTER_B_WP3_POST_MERGE_SHA256SUMS.txt'
EXPECTED_SUCCESSOR=['.github/workflows/gate3-cluster-b-wp3-post-merge-closeout.yml', 'docs/gate3/cluster_b/WP3_POST_MERGE_ARCHIVAL_CLOSEOUT_AND_DEVELOPMENT_BRANCH_SYNCHRONIZATION.md', 'release/v1.4.0/GATE3_CLUSTER_B_WP3_DEVELOPMENT_BRANCH_SYNCHRONIZATION_RECORD.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP3_POST_MERGE_ARCHIVAL_CLOSEOUT_RECORD.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP3_POST_MERGE_CLOSEOUT_GATES.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP3_POST_MERGE_FROZEN_UPSTREAM_PRESERVATION_RECORD.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP3_POST_MERGE_HOSTED_CI_EVIDENCE.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP3_POST_MERGE_SCHEMA_BUNDLE_MANIFEST.json', 'release/v1.4.0/tools/patch_wp3_post_merge_allowlist.py', 'schemas/v1.4.0/gate3_cluster_b_wp3_development_branch_synchronization_record.schema.json', 'schemas/v1.4.0/gate3_cluster_b_wp3_post_merge_archival_closeout_record.schema.json', 'schemas/v1.4.0/gate3_cluster_b_wp3_post_merge_closeout_gates.schema.json', 'schemas/v1.4.0/gate3_cluster_b_wp3_post_merge_frozen_upstream_preservation_record.schema.json', 'schemas/v1.4.0/gate3_cluster_b_wp3_post_merge_hosted_ci_evidence.schema.json', 'scripts/build_gate3_cluster_b_wp3_post_merge_closeout.py', 'scripts/capture_gate3_cluster_b_wp3_post_merge_evidence.py', 'scripts/synchronize_v1_4_0_development_wp3.sh', 'scripts/verify_gate3_cluster_b_wp3_post_merge_closeout.py', 'tests/test_gate3_cluster_b_wp3_post_merge_closeout.py', 'scripts/build_gate3_cluster_b_wp3.py', 'scripts/verify_gate3_cluster_b_wp3.py', 'scripts/verify_gate3_cluster_b_wp2.py', 'scripts/verify_gate3_cluster_b_wp2_post_merge_closeout.py', 'release/v1.4.0/GATE3_CLUSTER_B_WP2_POST_MERGE_SHA256SUMS.txt']
EXPECTED_CHANGED=['.github/workflows/gate3-cluster-b-wp3-post-merge-closeout.yml', 'docs/gate3/cluster_b/WP3_POST_MERGE_ARCHIVAL_CLOSEOUT_AND_DEVELOPMENT_BRANCH_SYNCHRONIZATION.md', 'release/v1.4.0/GATE3_CLUSTER_B_WP2_POST_MERGE_SHA256SUMS.txt', 'release/v1.4.0/GATE3_CLUSTER_B_WP3_DEVELOPMENT_BRANCH_SYNCHRONIZATION_RECORD.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP3_POST_MERGE_ARCHIVAL_CLOSEOUT_RECORD.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP3_POST_MERGE_CLOSEOUT_GATES.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP3_POST_MERGE_FROZEN_UPSTREAM_PRESERVATION_RECORD.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP3_POST_MERGE_HOSTED_CI_EVIDENCE.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP3_POST_MERGE_SCHEMA_BUNDLE_MANIFEST.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP3_POST_MERGE_SHA256SUMS.txt', 'release/v1.4.0/tools/patch_wp3_post_merge_allowlist.py', 'schemas/v1.4.0/gate3_cluster_b_wp3_development_branch_synchronization_record.schema.json', 'schemas/v1.4.0/gate3_cluster_b_wp3_post_merge_archival_closeout_record.schema.json', 'schemas/v1.4.0/gate3_cluster_b_wp3_post_merge_closeout_gates.schema.json', 'schemas/v1.4.0/gate3_cluster_b_wp3_post_merge_frozen_upstream_preservation_record.schema.json', 'schemas/v1.4.0/gate3_cluster_b_wp3_post_merge_hosted_ci_evidence.schema.json', 'scripts/build_gate3_cluster_b_wp3.py', 'scripts/build_gate3_cluster_b_wp3_post_merge_closeout.py', 'scripts/capture_gate3_cluster_b_wp3_post_merge_evidence.py', 'scripts/synchronize_v1_4_0_development_wp3.sh', 'scripts/verify_gate3_cluster_b_wp2.py', 'scripts/verify_gate3_cluster_b_wp2_post_merge_closeout.py', 'scripts/verify_gate3_cluster_b_wp3.py', 'scripts/verify_gate3_cluster_b_wp3_post_merge_closeout.py', 'tests/test_gate3_cluster_b_wp3_post_merge_closeout.py']
SUPERSEDED={'scripts/build_gate3_cluster_b_wp3.py','scripts/verify_gate3_cluster_b_wp3.py'}
IMMUTABLE_WP3={'release/v1.4.0/GATE3_CLUSTER_B_WP3_IPEC_V0_1_COMPATIBILITY_PROFILE.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP3_FIXTURE_MANIFEST.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP3_SCHEMA_BUNDLE_MANIFEST.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP3_SHA256SUMS.txt', 'release/v1.4.0/GATE3_CLUSTER_B_WP3_ADAPTER_BINDING_MANIFEST.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP3_BASELINE_LOCK.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP3_EXTENSION_RULE_REGISTRY_T157_T162.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP3_ACCEPTANCE_GATES.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP3_PRESERVATION_FIREWALL.json'}
PAIRS=[('release/v1.4.0/GATE3_CLUSTER_B_WP3_POST_MERGE_ARCHIVAL_CLOSEOUT_RECORD.json', 'schemas/v1.4.0/gate3_cluster_b_wp3_post_merge_archival_closeout_record.schema.json'), ('release/v1.4.0/GATE3_CLUSTER_B_WP3_DEVELOPMENT_BRANCH_SYNCHRONIZATION_RECORD.json', 'schemas/v1.4.0/gate3_cluster_b_wp3_development_branch_synchronization_record.schema.json'), ('release/v1.4.0/GATE3_CLUSTER_B_WP3_POST_MERGE_HOSTED_CI_EVIDENCE.json', 'schemas/v1.4.0/gate3_cluster_b_wp3_post_merge_hosted_ci_evidence.schema.json'), ('release/v1.4.0/GATE3_CLUSTER_B_WP3_POST_MERGE_FROZEN_UPSTREAM_PRESERVATION_RECORD.json', 'schemas/v1.4.0/gate3_cluster_b_wp3_post_merge_frozen_upstream_preservation_record.schema.json'), ('release/v1.4.0/GATE3_CLUSTER_B_WP3_POST_MERGE_CLOSEOUT_GATES.json', 'schemas/v1.4.0/gate3_cluster_b_wp3_post_merge_closeout_gates.schema.json')]
def load(rel): return json.loads((ROOT/rel).read_text(encoding='utf-8'))
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def ledger(path):
 out={}
 for line in path.read_text(encoding='utf-8').splitlines():
  if line.strip() and not line.lstrip().startswith('#'):
   d,r=line.split('  ',1); out[r]=d
 return out
def canonical_sha(obj):
 cp=json.loads(json.dumps(obj)); cp['canonical_sha256']=None
 return hashlib.sha256(json.dumps(cp,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def validate_records():
 errors=[]
 for doc,schema in PAIRS:
  try: Draft202012Validator(load(schema)).validate(load(doc))
  except Exception as exc: errors.append(f'schema failure {doc}: {exc}')
 close,sync,evidence,preserve,gates=[load(x[0]) for x in PAIRS]
 if close['merged_pr']!=25 or close['merge_commit']!=MERGE or close['accepted_head_commit']!=ACCEPTED: errors.append('merge identity mismatch')
 if close['hosted_ci_checks']!={'pass':29,'fail':0,'pending':0,'skipped':0,'total':29}: errors.append('hosted check summary mismatch')
 if close['wp3_acceptance_gates']!={'pass':24,'fail':0,'pending':0,'total':24}: errors.append('WP3 acceptance summary mismatch')
 if close['canonical_wp3_records_modified'] or close['canonical_wp3_ledger_modified'] or close['proof_or_new_runtime_semantics_added'] or close['wp4_proof_completion_authorized'] or any(close['release_actions'].values()): errors.append('closeout authorization firewall failure')
 if sync['canonical_wp3_merge_baseline']!=MERGE or sync['sync_mode']!='FAST_FORWARD_ONLY' or sync['ahead_by'] or sync['behind_by'] or sync['compare_status']!='identical': errors.append('synchronization record mismatch')
 if sync['force_push_authorized'] or sync['history_rewrite_authorized'] or sync['branch_deletion_authorized']: errors.append('synchronization authorization failure')
 if evidence['source_pr']!=25 or evidence['source_head_sha']!=ACCEPTED or evidence['merge_commit']!=MERGE or evidence['check_summary']!={'success':29,'failure':0,'pending':0,'skipped':0,'total':29} or evidence['canonical_sha256']!=canonical_sha(evidence): errors.append('hosted evidence mismatch')
 if preserve['canonical_wp3_records_modified'] or preserve['canonical_wp3_ledger_modified'] or preserve['fixture_count_preserved']!=15 or preserve['theorem_ids_preserved']!=[f'T{i}' for i in range(157,163)] or preserve['release_actions_authorized'] or preserve['proof_implementation_authorized'] or preserve['runtime_semantics_modified_by_closeout']: errors.append('preservation record mismatch')
 if gates['gate_count']!=21 or len(gates['gates'])!=21 or any(x['status']!='PASS' for x in gates['gates']): errors.append('closeout gate failure')
 man=load('release/v1.4.0/GATE3_CLUSTER_B_WP3_POST_MERGE_SCHEMA_BUNDLE_MANIFEST.json')
 if man.get('schema_count')!=5 or man.get('document_count')!=5: errors.append('schema bundle mismatch')
 return errors
def verify_ledger():
 if not HISTORICAL.is_file() or not SUCCESSOR.is_file(): return ['missing historical or successor WP3 ledger']
 h,s=ledger(HISTORICAL),ledger(SUCCESSOR); errors=[]
 if set(s)!=set(EXPECTED_SUCCESSOR): errors.append('successor ledger path set mismatch')
 if set(h)&set(s)!=SUPERSEDED: errors.append('unexpected historical/successor overlap: '+str(sorted(set(h)&set(s))))
 for rel,old in h.items():
  p=ROOT/rel
  if not p.is_file(): errors.append('historical file missing: '+rel); continue
  exp=s.get(rel) if rel in SUPERSEDED else old
  if digest(p)!=exp: errors.append('historical/successor hash mismatch: '+rel)
 for rel,exp in s.items():
  p=ROOT/rel
  if not p.is_file() or digest(p)!=exp: errors.append('successor hash mismatch: '+rel)
 return errors
def gitout(*args,check=True):
 cp=subprocess.run(['git',*args],cwd=ROOT,text=True,capture_output=True)
 if check and cp.returncode: raise RuntimeError(cp.stderr.strip())
 return cp.stdout.strip()
def git_checks(allow_main):
 errors=[]; branch=gitout('branch','--show-current',check=False); effective=branch or os.environ.get('GITHUB_HEAD_REF','') or os.environ.get('GITHUB_REF_NAME','')
 if effective!=DEV and not (allow_main and effective=='main'): errors.append('unexpected branch '+repr(effective))
 if subprocess.run(['git','merge-base','--is-ancestor',MERGE,'HEAD'],cwd=ROOT).returncode: errors.append('HEAD does not contain canonical WP3 merge baseline')
 if gitout('rev-parse','refs/tags/v1.3.0^{}')!=TAG_TARGET: errors.append('stable v1.3.0 tag target changed')
 changed=set(gitout('-c','core.quotePath=false','diff','--name-only','--no-renames',MERGE,'--',check=False).splitlines()); changed.update(gitout('-c','core.quotePath=false','ls-files','--others','--exclude-standard',check=False).splitlines()); changed.discard('')
 if changed!=set(EXPECTED_CHANGED): errors.append('closeout path set mismatch: missing='+str(sorted(set(EXPECTED_CHANGED)-changed))+', extra='+str(sorted(changed-set(EXPECTED_CHANGED))))
 if changed & IMMUTABLE_WP3: errors.append('canonical WP3 record or ledger changed: '+str(sorted(changed&IMMUTABLE_WP3)))
 for p in changed:
  if p.startswith('release/v1.4.0/GATE3_CLUSTER_B_WP0_') or p.startswith('release/v1.4.0/GATE3_CLUSTER_B_WP1_') or (p.startswith('release/v1.4.0/GATE3_CLUSTER_B_WP2_') and p!='release/v1.4.0/GATE3_CLUSTER_B_WP2_POST_MERGE_SHA256SUMS.txt'): errors.append('closed predecessor release record changed: '+p)
 return errors
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--package-only',action='store_true'); ap.add_argument('--allow-main',action='store_true'); a=ap.parse_args()
 errors=validate_records()+verify_ledger()
 if not a.package_only: errors+=git_checks(a.allow_main)
 print(json.dumps({'artifact':'V0_OSAP_GATE3_CLUSTER_B_WP3_POST_MERGE_CLOSEOUT','status':'PASS' if not errors else 'FAIL','merged_pr':25,'merge_commit':MERGE,'hosted_checks':'29/29 PASS','wp3_acceptance':'24/24 PASS','release_actions_authorized':False,'errors':errors},indent=2,sort_keys=True))
 return 0 if not errors else 1
if __name__=='__main__': raise SystemExit(main())
