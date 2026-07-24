#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, subprocess, sys
from pathlib import Path
from jsonschema import Draft202012Validator
ROOT=Path(__file__).resolve().parents[1]
BASE='b3798367af960ff3b588778966c5e233d89e72ab'; ACCEPTED='8a692859b2e02a8c9fccc008f76bb24218716f40'; MERGE='f984b59cec832307bac7270c7d437a789bec99ce'; DEV='v1.4.0-development'; TAG='13bf095688bcabd5b090f188e9bd28a16237edeb'
PAIRS=[('release/v1.4.0/GATE3_CLUSTER_B_WP6_POST_MERGE_ARCHIVAL_CLOSEOUT_RECORD.json', 'schemas/v1.4.0/gate3_cluster_b_wp6_post_merge_archival_closeout_record.schema.json'), ('release/v1.4.0/GATE3_CLUSTER_B_WP6_DEVELOPMENT_BRANCH_SYNCHRONIZATION_RECORD.json', 'schemas/v1.4.0/gate3_cluster_b_wp6_development_branch_synchronization_record.schema.json'), ('release/v1.4.0/GATE3_CLUSTER_B_WP6_POST_MERGE_HOSTED_CI_EVIDENCE.json', 'schemas/v1.4.0/gate3_cluster_b_wp6_post_merge_hosted_ci_evidence.schema.json'), ('release/v1.4.0/GATE3_CLUSTER_B_WP6_POST_MERGE_FROZEN_UPSTREAM_PRESERVATION_RECORD.json', 'schemas/v1.4.0/gate3_cluster_b_wp6_post_merge_frozen_upstream_preservation_record.schema.json'), ('release/v1.4.0/GATE3_CLUSTER_B_WP6_POST_MERGE_CLOSEOUT_GATES.json', 'schemas/v1.4.0/gate3_cluster_b_wp6_post_merge_closeout_gates.schema.json'), ('release/v1.4.0/GATE3_CLUSTER_B_WP6_POST_MERGE_SYNC_FIXTURE_MANIFEST.json', 'schemas/v1.4.0/gate3_cluster_b_wp6_post_merge_sync_fixture_manifest.schema.json')]
def run(*a,check=True,text=True):
    cp=subprocess.run(a,cwd=ROOT,capture_output=True,text=text,check=False)
    if check and cp.returncode:
        err=cp.stderr if text else cp.stderr.decode('utf-8',errors='replace'); raise RuntimeError(err.strip())
    return cp
def load(r): return json.loads((ROOT/r).read_text(encoding='utf-8'))
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def canonical_sha(o):
    cp=json.loads(json.dumps(o)); cp['canonical_sha256']=None
    return hashlib.sha256(json.dumps(cp,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
def check_wp6_frozen(errors):
    ledger_rel='release/v1.4.0/GATE3_CLUSTER_B_WP6_SHA256SUMS.txt'; ledger=ROOT/ledger_rel
    try:
        frozen=run('git','show',ACCEPTED+':'+ledger_rel,text=False).stdout
        if ledger.read_bytes()!=frozen: errors.append('canonical WP6 ledger modified')
        for line in ledger.read_text(encoding='utf-8').splitlines():
            if line.strip():
                h,rel=line.split('  ',1); p=ROOT/rel
                if not p.is_file() or digest(p)!=h: errors.append('WP6 frozen digest mismatch '+rel)
    except Exception as exc: errors.append('WP6 frozen ledger check failure: '+str(exc))
def main():
    p=argparse.ArgumentParser(); p.add_argument('--package-only',action='store_true'); a=p.parse_args(); errors=[]
    try:
        parents=run('git','show','-s','--format=%P',MERGE).stdout.strip().split()
        if parents!=[BASE,ACCEPTED]: errors.append('merge parent identity mismatch')
        if run('git','rev-parse',MERGE+'^{tree}').stdout.strip()!=run('git','rev-parse',ACCEPTED+'^{tree}').stdout.strip(): errors.append('merge tree mismatch')
        if run('git','rev-parse','v1.3.0^{}').stdout.strip()!=TAG: errors.append('stable tag target mismatch')
    except Exception as exc: errors.append('merge identity check failure: '+str(exc))
    if not a.package_only:
        try:
            if run('git','branch','--show-current').stdout.strip()!=DEV: errors.append('branch mismatch')
            if run('git','rev-parse','HEAD').stdout.strip()!=ACCEPTED: errors.append('pre-commit HEAD mismatch')
            if run('git','rev-parse','origin/main').stdout.strip()!=MERGE: errors.append('origin/main mismatch')
            if run('git','rev-parse','origin/'+DEV).stdout.strip()!=ACCEPTED: errors.append('origin/development mismatch')
            if run('git','rev-list','--left-right','--count','origin/main...origin/'+DEV).stdout.strip()!='1	0': errors.append('divergence mismatch')
        except Exception as exc: errors.append('live ref check failure: '+str(exc))
    for doc,sch in PAIRS:
        try: Draft202012Validator(load(sch)).validate(load(doc))
        except Exception as exc: errors.append('schema failure '+doc+': '+str(exc))
    close=load('release/v1.4.0/GATE3_CLUSTER_B_WP6_POST_MERGE_ARCHIVAL_CLOSEOUT_RECORD.json')
    sync=load('release/v1.4.0/GATE3_CLUSTER_B_WP6_DEVELOPMENT_BRANCH_SYNCHRONIZATION_RECORD.json')
    evidence=load('release/v1.4.0/GATE3_CLUSTER_B_WP6_POST_MERGE_HOSTED_CI_EVIDENCE.json')
    preserve=load('release/v1.4.0/GATE3_CLUSTER_B_WP6_POST_MERGE_FROZEN_UPSTREAM_PRESERVATION_RECORD.json')
    gates=load('release/v1.4.0/GATE3_CLUSTER_B_WP6_POST_MERGE_CLOSEOUT_GATES.json')
    if close['merged_pr']!=32 or close['canonical_merge_commit']!=MERGE or close['accepted_head_commit']!=ACCEPTED: errors.append('closeout identity mismatch')
    if close['hosted_wp6_audit']!={'run_id':30109896184,'status':'completed','conclusion':'success','dedicated_jobs_pass':10,'dedicated_jobs_total':10}: errors.append('hosted WP6 audit summary mismatch')
    if close['post_merge_local_verification']!={'pytest_passed':149,'pytest_skipped':6,'pytest_deselected':4,'proof_hole_scan':'PASS','return_code':0,'isolated_detached_worktree':True,'temporary_worktree_removed':True}: errors.append('local verification summary mismatch')
    if close['gate3_closed'] or any(close['authorization_firewall'].values()): errors.append('authorization firewall failure')
    if sync['canonical_wp6_merge_baseline']!=MERGE or sync['main_ahead_by']!=1 or sync['development_ahead_by']!=0: errors.append('sync record mismatch')
    if sync['force_push_authorized'] or sync['history_rewrite_authorized'] or sync['branch_deletion_authorized'] or sync['synchronization_executed']: errors.append('sync authorization failure')
    if evidence['canonical_sha256']!=canonical_sha(evidence) or evidence['source_pr']!=32 or evidence['check_summary']['success']!=10: errors.append('hosted evidence mismatch')
    if preserve['canonical_wp6_records_modified'] or preserve['canonical_wp6_ledger_modified'] or preserve['release_actions_authorized'] or preserve['gate3_close_authorized']: errors.append('preservation failure')
    if gates['gate_count']!=24 or any(x['status']!='PASS' for x in gates['gates']): errors.append('closeout gates failure')
    manifest=load('release/v1.4.0/GATE3_CLUSTER_B_WP6_POST_MERGE_SCHEMA_BUNDLE_MANIFEST.json')
    if manifest['schema_count']!=6 or manifest['document_count']!=6: errors.append('schema bundle count mismatch')
    for item in manifest['pairs']:
        if digest(ROOT/item['document'])!=item['document_sha256'] or digest(ROOT/item['schema'])!=item['schema_sha256']: errors.append('schema bundle hash mismatch '+item['document'])
    check_wp6_frozen(errors)
    try:
        run(sys.executable,'scripts/build_gate3_cluster_b_wp6_post_merge_closeout.py','--check')
        run(sys.executable,'scripts/replay_gate3_cluster_b_wp6_post_merge_sync.py')
        run(sys.executable,'release/v1.4.0/tools/patch_wp6_post_merge_allowlist.py')
    except Exception as exc: errors.append('builder/replay/allowlist failure: '+str(exc))
    result={'artifact':'V0_OSAP_GATE3_CLUSTER_B_WP6_POST_MERGE_CLOSEOUT','errors':errors,'canonical_merge_commit':MERGE,'merged_pr':32,'hosted_wp6_jobs':'10/10 PASS','local_regression':'149 passed, 6 skipped, 4 deselected','release_actions_authorized':False,'gate3_closed':False,'status':'PASS' if not errors else 'FAIL'}
    print(json.dumps(result,indent=2,sort_keys=True)); return 0 if not errors else 1
if __name__=='__main__': raise SystemExit(main())
