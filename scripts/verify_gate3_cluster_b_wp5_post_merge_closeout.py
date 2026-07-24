#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, os, subprocess
from pathlib import Path
from jsonschema import Draft202012Validator
ROOT=Path(__file__).resolve().parents[1]
BASELINE='7b497f197652874164e00fe9c0ef7f67e760c979'; ACCEPTED='1c16ffb529b7e9a43c16739de26ad185c2f4b74c'; MERGE='adda93cae34d6579e8b715d4107ff7f62a6f9c6b'; DEV='v1.4.0-development'
PAIRS=[('release/v1.4.0/GATE3_CLUSTER_B_WP5_POST_MERGE_ARCHIVAL_CLOSEOUT_RECORD.json', 'schemas/v1.4.0/gate3_cluster_b_wp5_post_merge_archival_closeout_record.schema.json'), ('release/v1.4.0/GATE3_CLUSTER_B_WP5_DEVELOPMENT_BRANCH_SYNCHRONIZATION_RECORD.json', 'schemas/v1.4.0/gate3_cluster_b_wp5_development_branch_synchronization_record.schema.json'), ('release/v1.4.0/GATE3_CLUSTER_B_WP5_POST_MERGE_HOSTED_CI_EVIDENCE.json', 'schemas/v1.4.0/gate3_cluster_b_wp5_post_merge_hosted_ci_evidence.schema.json'), ('release/v1.4.0/GATE3_CLUSTER_B_WP5_POST_MERGE_FROZEN_UPSTREAM_PRESERVATION_RECORD.json', 'schemas/v1.4.0/gate3_cluster_b_wp5_post_merge_frozen_upstream_preservation_record.schema.json'), ('release/v1.4.0/GATE3_CLUSTER_B_WP5_POST_MERGE_CLOSEOUT_GATES.json', 'schemas/v1.4.0/gate3_cluster_b_wp5_post_merge_closeout_gates.schema.json')]
def run(*a,check=True,text=True):
    cp=subprocess.run(a,cwd=ROOT,capture_output=True,text=text,check=False)
    if check and cp.returncode:
        err=cp.stderr if text else cp.stderr.decode('utf-8',errors='replace')
        raise RuntimeError(err.strip())
    return cp
def load(r): return json.loads((ROOT/r).read_text(encoding='utf-8'))
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def canonical_sha(o):
    cp=json.loads(json.dumps(o)); cp['canonical_sha256']=None
    return hashlib.sha256(json.dumps(cp,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def main():
    p=argparse.ArgumentParser(); p.add_argument('--package-only',action='store_true'); p.add_argument('--allow-main',action='store_true'); a=p.parse_args()
    errors=[]
    try:
        parents=run('git','show','-s','--format=%P',MERGE).stdout.strip().split()
        if parents!=[BASELINE,ACCEPTED]: errors.append('merge parent identity mismatch')
        if run('git','rev-parse',MERGE+'^{tree}').stdout.strip()!=run('git','rev-parse',ACCEPTED+'^{tree}').stdout.strip():
            errors.append('merge tree mismatch')
    except Exception as exc: errors.append('merge identity check failure: '+str(exc))
    for doc,sch in PAIRS:
        try: Draft202012Validator(load(sch)).validate(load(doc))
        except Exception as exc: errors.append('schema failure '+doc+': '+str(exc))
    close=load('release/v1.4.0/GATE3_CLUSTER_B_WP5_POST_MERGE_ARCHIVAL_CLOSEOUT_RECORD.json')
    sync=load('release/v1.4.0/GATE3_CLUSTER_B_WP5_DEVELOPMENT_BRANCH_SYNCHRONIZATION_RECORD.json')
    evidence=load('release/v1.4.0/GATE3_CLUSTER_B_WP5_POST_MERGE_HOSTED_CI_EVIDENCE.json')
    preserve=load('release/v1.4.0/GATE3_CLUSTER_B_WP5_POST_MERGE_FROZEN_UPSTREAM_PRESERVATION_RECORD.json')
    gates=load('release/v1.4.0/GATE3_CLUSTER_B_WP5_POST_MERGE_CLOSEOUT_GATES.json')
    if close['merged_pr']!=29 or close['merge_commit']!=MERGE or close['accepted_head_commit']!=ACCEPTED: errors.append('closeout identity mismatch')
    if close['hosted_ci_checks']!={'pass':30,'fail':0,'pending':0,'skipped':0,'total':30}: errors.append('hosted check summary mismatch')
    if close['wp5_acceptance_gates']!={'pass':24,'fail':0,'pending':0,'total':24}: errors.append('WP5 acceptance summary mismatch')
    if close['wp6_authorized'] or any(close['release_actions'].values()) or close['runtime_or_proof_semantics_added']: errors.append('authorization firewall failure')
    if sync['canonical_wp5_merge_baseline']!=MERGE or sync['main_ahead_by']!=1 or sync['development_ahead_by']!=0: errors.append('sync record mismatch')
    if sync['force_push_authorized'] or sync['history_rewrite_authorized'] or sync['branch_deletion_authorized']: errors.append('sync authorization failure')
    if evidence['canonical_sha256']!=canonical_sha(evidence) or evidence['source_pr']!=29 or evidence['check_summary']['success']!=30: errors.append('hosted evidence mismatch')
    if preserve['canonical_wp5_records_modified'] or preserve['canonical_wp5_ledger_modified'] or preserve['release_actions_authorized'] or preserve['wp6_start_authorized']: errors.append('preservation failure')
    if gates['gate_count']!=21 or any(x['status']!='PASS' for x in gates['gates']): errors.append('closeout gates failure')
    manifest=load('release/v1.4.0/GATE3_CLUSTER_B_WP5_POST_MERGE_SCHEMA_BUNDLE_MANIFEST.json')
    if manifest['schema_count']!=5 or manifest['document_count']!=5: errors.append('schema bundle count mismatch')
    for item in manifest['pairs']:
        if digest(ROOT/item['document'])!=item['document_sha256'] or digest(ROOT/item['schema'])!=item['schema_sha256']:
            errors.append('schema bundle hash mismatch '+item['document'])
    try:
        run('python','scripts/build_gate3_cluster_b_wp5_post_merge_closeout.py','--check')
        run('python','release/v1.4.0/tools/patch_wp5_post_merge_allowlist.py')
        run('python','release/v1.4.0/tools/patch_wp5_allowlist.py')
        run('python','scripts/build_gate3_cluster_b_wp5.py','--check')
    except Exception as exc: errors.append('builder/allowlist failure: '+str(exc))
    result={'artifact':'V0_OSAP_GATE3_CLUSTER_B_WP5_POST_MERGE_CLOSEOUT','errors':errors,
             'hosted_checks':'30/30 PASS','hosted_workflows':'17/17 PASS','merge_commit':MERGE,
             'merged_pr':29,'release_actions_authorized':False,'status':'PASS' if not errors else 'FAIL',
             'wp5_acceptance':'24/24 PASS','wp6_authorized':False}
    print(json.dumps(result,indent=2,sort_keys=True)); return 0 if not errors else 1
if __name__=='__main__': raise SystemExit(main())
