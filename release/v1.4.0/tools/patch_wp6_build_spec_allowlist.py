#!/usr/bin/env python3
from __future__ import annotations
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BASELINE = 'b3798367af960ff3b588778966c5e233d89e72ab'
TAG_TARGET = '13bf095688bcabd5b090f188e9bd28a16237edeb'
EXPECTED = ['docs/gate3/cluster_b/WP6_BUILD_SPECIFICATION.md', 'release/v1.4.0/GATE3_CLUSTER_B_WP6_BUILD_PLAN.json', 'release/v1.4.0/tools/patch_wp6_build_spec_allowlist.py', 'schemas/v1.4.0/gate3_cluster_b_wp6_build_plan.schema.json', 'scripts/verify_gate3_cluster_b_wp6_build_spec.py', 'tests/test_gate3_cluster_b_wp6_build_spec.py']

def run(*args: str, check: bool = True):
    cp = subprocess.run(args, cwd=ROOT, capture_output=True, text=True, check=False)
    if check and cp.returncode:
        raise SystemExit(cp.stdout + cp.stderr)
    return cp

def lines(*args: str) -> list[str]:
    return [x for x in run('git', *args).stdout.splitlines() if x]

def main() -> int:
    run('git','cat-file','-e',BASELINE+'^{commit}')
    if run('git','merge-base','--is-ancestor',BASELINE,'HEAD',check=False).returncode:
        raise SystemExit('WP6 build-spec baseline is not an ancestor of HEAD')
    changed=set(lines('diff','--name-only',BASELINE,'--'))
    changed.update(lines('ls-files','--others','--exclude-standard'))
    if changed != set(EXPECTED):
        raise SystemExit('WP6 BUILD-SPEC ALLOWLIST mismatch missing='+repr(sorted(set(EXPECTED)-changed))+' extra='+repr(sorted(changed-set(EXPECTED))))
    statuses={}
    for row in lines('diff','--name-status',BASELINE,'--'):
        code, rel = row.split('	',1); statuses[rel]=code
    for rel in lines('ls-files','--others','--exclude-standard'):
        statuses[rel]='A'
    if any(statuses.get(rel)!='A' for rel in EXPECTED):
        raise SystemExit('WP6 build-spec paths must be additive')
    if run('git','rev-parse','refs/tags/v1.3.0^{}').stdout.strip() != TAG_TARGET:
        raise SystemExit('stable v1.3.0 tag target changed')
    print('WP6 BUILD-SPEC EXACT CHANGED-PATH ALLOWLIST: PASS')
    return 0
if __name__ == '__main__':
    raise SystemExit(main())
