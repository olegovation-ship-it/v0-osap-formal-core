#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
LEDGER=ROOT/'release/v1.4.0/GATE3_CLUSTER_B_WP5_POST_MERGE_SHA256SUMS.txt'
INPUTS=['release/v1.4.0/tools/patch_wp5_allowlist.py', 'scripts/build_gate3_cluster_b_wp5.py', 'scripts/verify_gate3_cluster_b_wp5.py', '.github/workflows/gate3-cluster-b-wp5-post-merge-closeout.yml', 'docs/gate3/cluster_b/WP5_POST_MERGE_ARCHIVAL_CLOSEOUT_AND_DEVELOPMENT_BRANCH_SYNCHRONIZATION.md', 'release/v1.4.0/GATE3_CLUSTER_B_WP5_DEVELOPMENT_BRANCH_SYNCHRONIZATION_RECORD.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP5_POST_MERGE_ARCHIVAL_CLOSEOUT_RECORD.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP5_POST_MERGE_CLOSEOUT_GATES.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP5_POST_MERGE_FROZEN_UPSTREAM_PRESERVATION_RECORD.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP5_POST_MERGE_HOSTED_CI_EVIDENCE.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP5_POST_MERGE_SCHEMA_BUNDLE_MANIFEST.json', 'release/v1.4.0/tools/patch_wp5_post_merge_allowlist.py', 'schemas/v1.4.0/gate3_cluster_b_wp5_development_branch_synchronization_record.schema.json', 'schemas/v1.4.0/gate3_cluster_b_wp5_post_merge_archival_closeout_record.schema.json', 'schemas/v1.4.0/gate3_cluster_b_wp5_post_merge_closeout_gates.schema.json', 'schemas/v1.4.0/gate3_cluster_b_wp5_post_merge_frozen_upstream_preservation_record.schema.json', 'schemas/v1.4.0/gate3_cluster_b_wp5_post_merge_hosted_ci_evidence.schema.json', 'scripts/build_gate3_cluster_b_wp5_post_merge_closeout.py', 'scripts/capture_gate3_cluster_b_wp5_post_merge_evidence.py', 'scripts/synchronize_v1_4_0_development_wp5.sh', 'scripts/verify_gate3_cluster_b_wp5_post_merge_closeout.py', 'tests/test_gate3_cluster_b_wp5_post_merge_closeout.py']
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def canonical_json(p):
    obj=json.loads(p.read_text(encoding='utf-8'))
    return p.read_text(encoding='utf-8')==json.dumps(obj,indent=2,sort_keys=True,ensure_ascii=False)+'\n'
def expected():
    missing=[r for r in INPUTS if not (ROOT/r).is_file()]
    if missing: raise SystemExit('missing WP5 post-merge closeout inputs: '+', '.join(missing))
    bad=[r for r in INPUTS if r.endswith('.json') and not canonical_json(ROOT/r)]
    if bad: raise SystemExit('non-canonical JSON: '+', '.join(bad))
    return ''.join(f'{digest(ROOT/r)}  {r}\n' for r in sorted(INPUTS))
def main():
    p=argparse.ArgumentParser(); p.add_argument('--check',action='store_true'); a=p.parse_args()
    exp=expected()
    if a.check:
        if not LEDGER.is_file() or LEDGER.read_text(encoding='utf-8')!=exp: raise SystemExit('WP5 post-merge SHA-256 ledger mismatch')
        print(f'WP5 POST-MERGE BUILD CHECK: PASS ({len(INPUTS)} hashed files)')
    else:
        LEDGER.write_text(exp,encoding='utf-8',newline='\n')
        print(f'WP5 POST-MERGE LEDGER WRITTEN: {len(INPUTS)} files')
    return 0
if __name__=='__main__': raise SystemExit(main())
