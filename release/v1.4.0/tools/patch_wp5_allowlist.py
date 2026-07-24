#!/usr/bin/env python3
from __future__ import annotations
import subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
BASELINE='7b497f197652874164e00fe9c0ef7f67e760c979'; TAG_TARGET='13bf095688bcabd5b090f188e9bd28a16237edeb'
EXPECTED=['.github/workflows/gate3-cluster-b-wp5.yml', 'docs/gate3/cluster_b/WP5_BUILD_SPECIFICATION.md', 'docs/gate3/cluster_b/WP5_CI_INTEGRATION_AND_DETERMINISTIC_EVIDENCE_MANIFESTS.md', 'fixtures/gate3/cluster_b/wp5/01_valid_canonical_evidence.json', 'fixtures/gate3/cluster_b/wp5/02_unordered_evidence_paths_rejected.json', 'fixtures/gate3/cluster_b/wp5/03_duplicate_evidence_path_rejected.json', 'fixtures/gate3/cluster_b/wp5/04_sha256_mismatch_rejected.json', 'fixtures/gate3/cluster_b/wp5/05_predecessor_chain_break_rejected.json', 'fixtures/gate3/cluster_b/wp5/06_release_action_rejected.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP5_ACCEPTANCE_GATES.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP5_BASELINE_LOCK.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP5_BUILD_PLAN.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP5_CI_JOB_MATRIX.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP5_EVIDENCE_INPUT_MANIFEST.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP5_FIXTURE_MANIFEST.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP5_PRESERVATION_FIREWALL.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP5_REPLAY_RECORD.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP5_SCHEMA_BUNDLE_MANIFEST.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP5_SHA256SUMS.txt', 'release/v1.4.0/tools/patch_wp5_allowlist.py', 'release/v1.4.0/tools/patch_wp5_build_spec_allowlist.py', 'schemas/v1.4.0/gate3_cluster_b_wp5_acceptance_gates.schema.json', 'schemas/v1.4.0/gate3_cluster_b_wp5_baseline_lock.schema.json', 'schemas/v1.4.0/gate3_cluster_b_wp5_build_plan.schema.json', 'schemas/v1.4.0/gate3_cluster_b_wp5_ci_job_matrix.schema.json', 'schemas/v1.4.0/gate3_cluster_b_wp5_evidence_fixture.schema.json', 'schemas/v1.4.0/gate3_cluster_b_wp5_evidence_input_manifest.schema.json', 'schemas/v1.4.0/gate3_cluster_b_wp5_fixture_manifest.schema.json', 'schemas/v1.4.0/gate3_cluster_b_wp5_preservation_firewall.schema.json', 'schemas/v1.4.0/gate3_cluster_b_wp5_replay_record.schema.json', 'schemas/v1.4.0/gate3_cluster_b_wp5_schema_bundle_manifest.schema.json', 'scripts/build_gate3_cluster_b_wp5.py', 'scripts/replay_gate3_cluster_b_wp5.py', 'scripts/verify_gate3_cluster_b_wp5.py', 'scripts/verify_gate3_cluster_b_wp5_build_spec.py', 'tests/test_gate3_cluster_b_wp5.py', 'tests/test_gate3_cluster_b_wp5_build_spec.py']
FORBIDDEN_PREFIXES=('checker/','lean/','coq/','release/v1.4.0/GATE3_CLUSTER_B_WP0_','release/v1.4.0/GATE3_CLUSTER_B_WP1_','release/v1.4.0/GATE3_CLUSTER_B_WP2_','release/v1.4.0/GATE3_CLUSTER_B_WP3_','release/v1.4.0/GATE3_CLUSTER_B_WP4_')
def run(*args: str, check: bool=True):
    cp=subprocess.run(args,cwd=ROOT,capture_output=True,text=True,check=False)
    if check and cp.returncode: raise SystemExit(cp.stdout+cp.stderr)
    return cp
def lines(*args: str): return [x for x in run('git',*args).stdout.splitlines() if x]
def main() -> int:
    run('git','cat-file','-e',BASELINE+'^{commit}')
    if run('git','merge-base','--is-ancestor',BASELINE,'HEAD',check=False).returncode: raise SystemExit('WP5 baseline is not an ancestor of HEAD')
    changed=set(lines('diff','--name-only',BASELINE,'--')); changed.update(lines('ls-files','--others','--exclude-standard'))
    if changed != set(EXPECTED): raise SystemExit('FAIL_WP5_ALLOWLIST missing='+repr(sorted(set(EXPECTED)-changed))+', extra='+repr(sorted(changed-set(EXPECTED))))
    if any(p.startswith(FORBIDDEN_PREFIXES) for p in changed): raise SystemExit('frozen or semantic predecessor path changed')
    statuses={}
    for row in lines('diff','--name-status',BASELINE,'--'):
        code,rel=row.split('	',1); statuses[rel]=code
    for rel in lines('ls-files','--others','--exclude-standard'): statuses[rel]='A'
    bad={rel:statuses.get(rel) for rel in EXPECTED if statuses.get(rel)!='A'}
    if bad: raise SystemExit('WP5 paths must be additive: '+repr(bad))
    if run('git','rev-parse','refs/tags/v1.3.0^{}').stdout.strip()!=TAG_TARGET: raise SystemExit('stable tag target changed')
    executable=[p for p in EXPECTED if p.endswith(('.py','.yml','.yaml','.sh'))]
    forbidden_commands=('git push','git tag','gh release','zenodo','force-push','git reset --hard','git rebase')
    for rel in executable:
        text=(ROOT/rel).read_text(encoding='utf-8').lower()
        # Documentation strings naming prohibitions are allowed only outside executable surfaces.
        for token in forbidden_commands:
            if token in text and rel.endswith(('.yml','.yaml','.sh')):
                raise SystemExit('forbidden executable command token '+token+' in '+rel)
    print('WP5 EXACT CHANGED-PATH ALLOWLIST: PASS ('+str(len(EXPECTED))+' additive paths)')
    return 0
if __name__=='__main__': raise SystemExit(main())
