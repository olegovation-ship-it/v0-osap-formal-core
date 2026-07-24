#!/usr/bin/env python3
from __future__ import annotations
import hashlib, subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
BASELINE='7b497f197652874164e00fe9c0ef7f67e760c979'; ACCEPTED='1c16ffb529b7e9a43c16739de26ad185c2f4b74c'; MERGE='adda93cae34d6579e8b715d4107ff7f62a6f9c6b'; TAG_TARGET='13bf095688bcabd5b090f188e9bd28a16237edeb'
CANONICAL_PATHS=['.github/workflows/gate3-cluster-b-wp5.yml', 'docs/gate3/cluster_b/WP5_BUILD_SPECIFICATION.md', 'docs/gate3/cluster_b/WP5_CI_INTEGRATION_AND_DETERMINISTIC_EVIDENCE_MANIFESTS.md', 'fixtures/gate3/cluster_b/wp5/01_valid_canonical_evidence.json', 'fixtures/gate3/cluster_b/wp5/02_unordered_evidence_paths_rejected.json', 'fixtures/gate3/cluster_b/wp5/03_duplicate_evidence_path_rejected.json', 'fixtures/gate3/cluster_b/wp5/04_sha256_mismatch_rejected.json', 'fixtures/gate3/cluster_b/wp5/05_predecessor_chain_break_rejected.json', 'fixtures/gate3/cluster_b/wp5/06_release_action_rejected.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP5_ACCEPTANCE_GATES.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP5_BASELINE_LOCK.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP5_BUILD_PLAN.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP5_CI_JOB_MATRIX.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP5_EVIDENCE_INPUT_MANIFEST.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP5_FIXTURE_MANIFEST.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP5_PRESERVATION_FIREWALL.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP5_REPLAY_RECORD.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP5_SCHEMA_BUNDLE_MANIFEST.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP5_SHA256SUMS.txt', 'release/v1.4.0/tools/patch_wp5_allowlist.py', 'release/v1.4.0/tools/patch_wp5_build_spec_allowlist.py', 'schemas/v1.4.0/gate3_cluster_b_wp5_acceptance_gates.schema.json', 'schemas/v1.4.0/gate3_cluster_b_wp5_baseline_lock.schema.json', 'schemas/v1.4.0/gate3_cluster_b_wp5_build_plan.schema.json', 'schemas/v1.4.0/gate3_cluster_b_wp5_ci_job_matrix.schema.json', 'schemas/v1.4.0/gate3_cluster_b_wp5_evidence_fixture.schema.json', 'schemas/v1.4.0/gate3_cluster_b_wp5_evidence_input_manifest.schema.json', 'schemas/v1.4.0/gate3_cluster_b_wp5_fixture_manifest.schema.json', 'schemas/v1.4.0/gate3_cluster_b_wp5_preservation_firewall.schema.json', 'schemas/v1.4.0/gate3_cluster_b_wp5_replay_record.schema.json', 'schemas/v1.4.0/gate3_cluster_b_wp5_schema_bundle_manifest.schema.json', 'scripts/build_gate3_cluster_b_wp5.py', 'scripts/replay_gate3_cluster_b_wp5.py', 'scripts/verify_gate3_cluster_b_wp5.py', 'scripts/verify_gate3_cluster_b_wp5_build_spec.py', 'tests/test_gate3_cluster_b_wp5.py', 'tests/test_gate3_cluster_b_wp5_build_spec.py']
CONTROLLED=['release/v1.4.0/tools/patch_wp5_allowlist.py', 'scripts/build_gate3_cluster_b_wp5.py', 'scripts/verify_gate3_cluster_b_wp5.py']
POST_MERGE_NEW=['.github/workflows/gate3-cluster-b-wp5-post-merge-closeout.yml', 'docs/gate3/cluster_b/WP5_POST_MERGE_ARCHIVAL_CLOSEOUT_AND_DEVELOPMENT_BRANCH_SYNCHRONIZATION.md', 'release/v1.4.0/GATE3_CLUSTER_B_WP5_DEVELOPMENT_BRANCH_SYNCHRONIZATION_RECORD.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP5_POST_MERGE_ARCHIVAL_CLOSEOUT_RECORD.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP5_POST_MERGE_CLOSEOUT_GATES.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP5_POST_MERGE_FROZEN_UPSTREAM_PRESERVATION_RECORD.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP5_POST_MERGE_HOSTED_CI_EVIDENCE.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP5_POST_MERGE_SCHEMA_BUNDLE_MANIFEST.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP5_POST_MERGE_SHA256SUMS.txt', 'release/v1.4.0/tools/patch_wp5_post_merge_allowlist.py', 'schemas/v1.4.0/gate3_cluster_b_wp5_development_branch_synchronization_record.schema.json', 'schemas/v1.4.0/gate3_cluster_b_wp5_post_merge_archival_closeout_record.schema.json', 'schemas/v1.4.0/gate3_cluster_b_wp5_post_merge_closeout_gates.schema.json', 'schemas/v1.4.0/gate3_cluster_b_wp5_post_merge_frozen_upstream_preservation_record.schema.json', 'schemas/v1.4.0/gate3_cluster_b_wp5_post_merge_hosted_ci_evidence.schema.json', 'scripts/build_gate3_cluster_b_wp5_post_merge_closeout.py', 'scripts/capture_gate3_cluster_b_wp5_post_merge_evidence.py', 'scripts/synchronize_v1_4_0_development_wp5.sh', 'scripts/verify_gate3_cluster_b_wp5_post_merge_closeout.py', 'tests/test_gate3_cluster_b_wp5_post_merge_closeout.py']
CANONICAL_LEDGER=ROOT/'release/v1.4.0/GATE3_CLUSTER_B_WP5_SHA256SUMS.txt'
SUCCESSOR_LEDGER=ROOT/'release/v1.4.0/GATE3_CLUSTER_B_WP5_POST_MERGE_SHA256SUMS.txt'
def run(*a,check=True,text=True):
    cp=subprocess.run(a,cwd=ROOT,capture_output=True,text=text,check=False)
    if check and cp.returncode:
        err=cp.stderr if text else cp.stderr.decode('utf-8',errors='replace')
        raise SystemExit('command failed: '+' '.join(a)+'\n'+err)
    return cp
def lines(*a): return [x for x in run('git',*a).stdout.splitlines() if x]
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def ledger(p):
    out={}
    for line in p.read_text(encoding='utf-8').splitlines():
        if line.strip():
            h,r=line.split('  ',1); out[r]=h
    return out
def main():
    for c in (BASELINE,ACCEPTED,MERGE): run('git','cat-file','-e',c+'^{commit}')
    parents=run('git','show','-s','--format=%P',MERGE).stdout.strip().split()
    if parents!=[BASELINE,ACCEPTED]: raise SystemExit('WP5 merge parent identity mismatch: '+repr(parents))
    if run('git','rev-parse',MERGE+'^{tree}').stdout.strip()!=run('git','rev-parse',ACCEPTED+'^{tree}').stdout.strip():
        raise SystemExit('WP5 merge tree differs from accepted head tree')
    expected=set(CANONICAL_PATHS)|set(POST_MERGE_NEW)
    changed=set(lines('diff','--name-only',BASELINE,'--')); changed.update(lines('ls-files','--others','--exclude-standard'))
    if changed!=expected:
        raise SystemExit('FAIL_WP5_ALLOWLIST missing='+repr(sorted(expected-changed))+', extra='+repr(sorted(changed-expected)))
    if not CANONICAL_LEDGER.is_file() or not SUCCESSOR_LEDGER.is_file(): raise SystemExit('missing canonical or successor WP5 ledger')
    old=ledger(CANONICAL_LEDGER); new=ledger(SUCCESSOR_LEDGER)
    historical=run('git','show',f'{MERGE}:release/v1.4.0/GATE3_CLUSTER_B_WP5_SHA256SUMS.txt',text=False).stdout
    if CANONICAL_LEDGER.read_bytes()!=historical: raise SystemExit('canonical WP5 ledger modified')
    if set(old)&set(new)!=set(CONTROLLED): raise SystemExit('unexpected canonical/successor overlap')
    for rel,h in old.items():
        p=ROOT/rel; expected_hash=new.get(rel,h)
        if not p.is_file() or digest(p)!=expected_hash: raise SystemExit('WP5 canonical/successor hash mismatch: '+rel)
    for rel,h in new.items():
        p=ROOT/rel
        if not p.is_file() or digest(p)!=h: raise SystemExit('WP5 successor hash mismatch: '+rel)
    if run('git','rev-parse','refs/tags/v1.3.0^{}').stdout.strip()!=TAG_TARGET: raise SystemExit('stable tag target changed')
    print('WP5 EXACT CHANGED-PATH ALLOWLIST: PASS (post-merge successor compatible)')
    return 0
if __name__=='__main__': raise SystemExit(main())
