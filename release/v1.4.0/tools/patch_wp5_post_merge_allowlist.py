#!/usr/bin/env python3
from __future__ import annotations
import subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
BASELINE='7b497f197652874164e00fe9c0ef7f67e760c979'; ACCEPTED='1c16ffb529b7e9a43c16739de26ad185c2f4b74c'; MERGE='adda93cae34d6579e8b715d4107ff7f62a6f9c6b'; TAG_TARGET='13bf095688bcabd5b090f188e9bd28a16237edeb'
CONTROLLED=['release/v1.4.0/tools/patch_wp5_allowlist.py', 'scripts/build_gate3_cluster_b_wp5.py', 'scripts/verify_gate3_cluster_b_wp5.py']; NEW=['.github/workflows/gate3-cluster-b-wp5-post-merge-closeout.yml', 'docs/gate3/cluster_b/WP5_POST_MERGE_ARCHIVAL_CLOSEOUT_AND_DEVELOPMENT_BRANCH_SYNCHRONIZATION.md', 'release/v1.4.0/GATE3_CLUSTER_B_WP5_DEVELOPMENT_BRANCH_SYNCHRONIZATION_RECORD.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP5_POST_MERGE_ARCHIVAL_CLOSEOUT_RECORD.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP5_POST_MERGE_CLOSEOUT_GATES.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP5_POST_MERGE_FROZEN_UPSTREAM_PRESERVATION_RECORD.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP5_POST_MERGE_HOSTED_CI_EVIDENCE.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP5_POST_MERGE_SCHEMA_BUNDLE_MANIFEST.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP5_POST_MERGE_SHA256SUMS.txt', 'release/v1.4.0/tools/patch_wp5_post_merge_allowlist.py', 'schemas/v1.4.0/gate3_cluster_b_wp5_development_branch_synchronization_record.schema.json', 'schemas/v1.4.0/gate3_cluster_b_wp5_post_merge_archival_closeout_record.schema.json', 'schemas/v1.4.0/gate3_cluster_b_wp5_post_merge_closeout_gates.schema.json', 'schemas/v1.4.0/gate3_cluster_b_wp5_post_merge_frozen_upstream_preservation_record.schema.json', 'schemas/v1.4.0/gate3_cluster_b_wp5_post_merge_hosted_ci_evidence.schema.json', 'scripts/build_gate3_cluster_b_wp5_post_merge_closeout.py', 'scripts/capture_gate3_cluster_b_wp5_post_merge_evidence.py', 'scripts/synchronize_v1_4_0_development_wp5.sh', 'scripts/verify_gate3_cluster_b_wp5_post_merge_closeout.py', 'tests/test_gate3_cluster_b_wp5_post_merge_closeout.py']; EXPECTED=set(CONTROLLED)|set(NEW)
def run(*a,check=True,text=True):
    cp=subprocess.run(a,cwd=ROOT,capture_output=True,text=text,check=False)
    if check and cp.returncode:
        err=cp.stderr if text else cp.stderr.decode('utf-8',errors='replace')
        raise SystemExit('command failed: '+' '.join(a)+'\n'+err)
    return cp
def lines(*a): return [x for x in run('git',*a).stdout.splitlines() if x]
def main():
    for c in (BASELINE,ACCEPTED,MERGE): run('git','cat-file','-e',c+'^{commit}')
    if run('git','show','-s','--format=%P',MERGE).stdout.strip().split()!=[BASELINE,ACCEPTED]:
        raise SystemExit('WP5 merge parent identity mismatch')
    if run('git','rev-parse',MERGE+'^{tree}').stdout.strip()!=run('git','rev-parse',ACCEPTED+'^{tree}').stdout.strip():
        raise SystemExit('WP5 merge and accepted-head trees differ')
    changed=set(lines('diff','--name-only',MERGE,'--')); changed.update(lines('ls-files','--others','--exclude-standard'))
    if changed!=EXPECTED:
        raise SystemExit('FAIL_WP5_POST_MERGE_ALLOWLIST missing='+repr(sorted(EXPECTED-changed))+', extra='+repr(sorted(changed-EXPECTED)))
    statuses={}
    for row in lines('diff','--name-status',MERGE,'--'):
        code,rel=row.split('\t',1); statuses[rel]=code
    for rel in lines('ls-files','--others','--exclude-standard'): statuses[rel]='A'
    for rel in CONTROLLED:
        if statuses.get(rel)!='M': raise SystemExit('controlled successor path status mismatch: '+rel)
    for rel in NEW:
        if statuses.get(rel)!='A': raise SystemExit('additive closeout path status mismatch: '+rel)
    for rel in lines('ls-tree','-r','--name-only',MERGE):
        if rel in CONTROLLED: continue
        p=ROOT/rel
        if not p.is_file(): raise SystemExit('merge-baseline path missing: '+rel)
        if p.read_bytes()!=run('git','show',f'{MERGE}:{rel}',text=False).stdout:
            raise SystemExit('frozen merge-baseline path modified: '+rel)
    if run('git','rev-parse','refs/tags/v1.3.0^{}').stdout.strip()!=TAG_TARGET: raise SystemExit('stable tag target changed')
    print('WP5 POST-MERGE EXACT CHANGED-PATH ALLOWLIST: PASS (23 paths)')
    return 0
if __name__=='__main__': raise SystemExit(main())
