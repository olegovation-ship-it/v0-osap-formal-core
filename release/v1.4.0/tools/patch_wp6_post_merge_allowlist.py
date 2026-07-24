#!/usr/bin/env python3
from __future__ import annotations
import subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
BASELINE='8a692859b2e02a8c9fccc008f76bb24218716f40'
EXPECTED=['.github/workflows/gate3-cluster-b-wp6-post-merge-closeout.yml', 'docs/gate3/cluster_b/WP6_POST_MERGE_ARCHIVAL_CLOSEOUT_AND_DEVELOPMENT_BRANCH_SYNCHRONIZATION.md', 'fixtures/gate3/cluster_b/wp6_post_merge_sync/00_identical_0_0.json', 'fixtures/gate3/cluster_b/wp6_post_merge_sync/01_main_ahead_1_0.json', 'fixtures/gate3/cluster_b/wp6_post_merge_sync/02_main_ahead_2_0.json', 'fixtures/gate3/cluster_b/wp6_post_merge_sync/03_development_ahead_0_1_rejected.json', 'fixtures/gate3/cluster_b/wp6_post_merge_sync/04_diverged_1_1_rejected.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP6_DEVELOPMENT_BRANCH_SYNCHRONIZATION_RECORD.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP6_POST_MERGE_ARCHIVAL_CLOSEOUT_RECORD.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP6_POST_MERGE_CLOSEOUT_GATES.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP6_POST_MERGE_FROZEN_UPSTREAM_PRESERVATION_RECORD.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP6_POST_MERGE_HOSTED_CI_EVIDENCE.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP6_POST_MERGE_SCHEMA_BUNDLE_MANIFEST.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP6_POST_MERGE_SHA256SUMS.txt', 'release/v1.4.0/GATE3_CLUSTER_B_WP6_POST_MERGE_SYNC_FIXTURE_MANIFEST.json', 'release/v1.4.0/tools/patch_wp6_post_merge_allowlist.py', 'schemas/v1.4.0/gate3_cluster_b_wp6_development_branch_synchronization_record.schema.json', 'schemas/v1.4.0/gate3_cluster_b_wp6_post_merge_archival_closeout_record.schema.json', 'schemas/v1.4.0/gate3_cluster_b_wp6_post_merge_closeout_gates.schema.json', 'schemas/v1.4.0/gate3_cluster_b_wp6_post_merge_frozen_upstream_preservation_record.schema.json', 'schemas/v1.4.0/gate3_cluster_b_wp6_post_merge_hosted_ci_evidence.schema.json', 'schemas/v1.4.0/gate3_cluster_b_wp6_post_merge_sync_fixture.schema.json', 'schemas/v1.4.0/gate3_cluster_b_wp6_post_merge_sync_fixture_manifest.schema.json', 'scripts/build_gate3_cluster_b_wp6_post_merge_closeout.py', 'scripts/capture_gate3_cluster_b_wp6_post_merge_evidence.py', 'scripts/classify_v1_4_0_development_sync_relation_wp6.py', 'scripts/replay_gate3_cluster_b_wp6_post_merge_sync.py', 'scripts/synchronize_v1_4_0_development_wp6.sh', 'scripts/verify_gate3_cluster_b_wp6_post_merge_closeout.py', 'tests/test_gate3_cluster_b_wp6_post_merge_closeout.py']
FORBIDDEN=('checker/','lean/','coq/','release/v1.4.0/RC','release/v1.4.0/FINAL','zenodo','doi','tag')
def run(*a,check=True):
    cp=subprocess.run(a,cwd=ROOT,capture_output=True,text=True,check=False)
    if check and cp.returncode: raise SystemExit(cp.stdout+cp.stderr)
    return cp

def status_entries():
    cp=run('git','status','--porcelain=v1','--untracked-files=all')
    entries=[]
    for line in cp.stdout.splitlines():
        if len(line)<4: raise SystemExit('malformed git status entry: '+repr(line))
        code=line[:2]; path=line[3:]
        if ' -> ' in path: raise SystemExit('rename/copy status is forbidden: '+line)
        entries.append((code,path))
    return entries

def main():
    entries=status_entries()
    actual=sorted(path for _,path in entries)
    if actual!=EXPECTED:
        missing=sorted(set(EXPECTED)-set(actual)); extra=sorted(set(actual)-set(EXPECTED))
        raise SystemExit('WP6 post-merge allowlist mismatch\nmissing='+repr(missing)+'\nextra='+repr(extra))
    non_additive=sorted((code,path) for code,path in entries if code!='??')
    if non_additive:
        raise SystemExit('WP6 post-merge payload must remain exact additive untracked files before commit: '+repr(non_additive))
    for p in actual:
        low=p.lower()
        if any(x.lower() in low for x in FORBIDDEN): raise SystemExit('forbidden release/publication/proof path: '+p)
        cp=subprocess.run(['git','diff','--no-index','--check','--','/dev/null',p],cwd=ROOT,capture_output=True,text=True,check=False)
        if cp.returncode not in (0,1):
            raise SystemExit((cp.stdout+cp.stderr).strip() or ('whitespace check failed: '+p))
    print(f'WP6 POST-MERGE ALLOWLIST: PASS ({len(actual)} exact additive untracked paths, no forbidden mutation)')
    return 0
if __name__=='__main__': raise SystemExit(main())
