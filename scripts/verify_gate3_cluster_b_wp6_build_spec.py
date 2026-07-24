#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, os, subprocess
from pathlib import Path
from jsonschema import Draft202012Validator

ROOT=Path(__file__).resolve().parents[1]
BASELINE='b3798367af960ff3b588778966c5e233d89e72ab'; BRANCH='v1.4.0-development'; TAG_TARGET='13bf095688bcabd5b090f188e9bd28a16237edeb'

def load(rel: str):
    return json.loads((ROOT/rel).read_text(encoding='utf-8'))

def run(*args: str, check: bool=True):
    cp=subprocess.run(args,cwd=ROOT,capture_output=True,text=True,check=False)
    if check and cp.returncode:
        raise SystemExit(cp.stdout+cp.stderr)
    return cp

def validate_plan() -> None:
    plan=load('release/v1.4.0/GATE3_CLUSTER_B_WP6_BUILD_PLAN.json')
    schema=load('schemas/v1.4.0/gate3_cluster_b_wp6_build_plan.schema.json')
    errors=sorted(Draft202012Validator(schema).iter_errors(plan),key=lambda e:list(e.path))
    if errors:
        raise SystemExit('WP6 build-plan schema failure: '+errors[0].message)
    if plan['new_theorem_ids'] or plan['ci_job_count'] != 10 or plan['audit_fixture_count'] != 14 or plan['acceptance_gate_count'] != 24:
        raise SystemExit('WP6 build-plan cardinality or theorem-scope failure')
    if plan['implementation_changed_path_allowlist'] != sorted(plan['implementation_changed_path_allowlist']):
        raise SystemExit('implementation allowlist is not sorted')
    if plan['build_spec_changed_path_allowlist'] != sorted(plan['build_spec_changed_path_allowlist']):
        raise SystemExit('build-spec allowlist is not sorted')
    forbidden=('checker/','lean/','coq/','fixtures/gate3/cluster_b/wp0','fixtures/gate3/cluster_b/wp1','fixtures/gate3/cluster_b/wp2','fixtures/gate3/cluster_b/wp3','fixtures/gate3/cluster_b/wp4','fixtures/gate3/cluster_b/wp5','release/v1.4.0/GATE3_CLUSTER_B_WP0_','release/v1.4.0/GATE3_CLUSTER_B_WP1_','release/v1.4.0/GATE3_CLUSTER_B_WP2_','release/v1.4.0/GATE3_CLUSTER_B_WP3_','release/v1.4.0/GATE3_CLUSTER_B_WP4_','release/v1.4.0/GATE3_CLUSTER_B_WP5_')
    bad=[p for p in plan['implementation_changed_path_allowlist'] if p.startswith(forbidden)]
    if bad:
        raise SystemExit('frozen predecessor or non-WP6 path in implementation allowlist: '+repr(bad))
    if any('/wp6/' not in p and 'WP6_' not in p and 'wp6_' not in p and 'wp6.' not in p and 'gate3-cluster-b-wp6.yml' not in p for p in plan['implementation_changed_path_allowlist']):
        raise SystemExit('non-WP6-prefixed implementation path detected')
    if plan['release_authorization'] != 'NONE' or plan['gate3_close_authorization'] != 'NONE':
        raise SystemExit('release or Gate 3 close authorization present')
    if plan['decision_candidate_values'] != ['ELIGIBLE_FOR_CLOSE_GATE3_PENDING_EXPLICIT_AUTHORIZATION','HOLD_WITH_EXPLICIT_BLOCKERS']:
        raise SystemExit('decision-candidate perimeter mismatch')

def git_checks(package_only: bool, integrated: bool) -> None:
    if package_only:
        return
    branch=run('git','branch','--show-current',check=False).stdout.strip() or os.environ.get('GITHUB_HEAD_REF','') or os.environ.get('GITHUB_REF_NAME','')
    if branch and branch != BRANCH and os.environ.get('GITHUB_ACTIONS')!='true':
        raise SystemExit('unexpected branch '+repr(branch))
    head=run('git','rev-parse','HEAD').stdout.strip()
    if run('git','merge-base','--is-ancestor',BASELINE,head,check=False).returncode:
        raise SystemExit('WP6 build-spec baseline is not an ancestor of HEAD')
    if os.environ.get('GITHUB_ACTIONS')!='true':
        if head!=BASELINE:
            raise SystemExit('WP6 build-spec local baseline mismatch')
        for ref in ('origin/main','origin/'+BRANCH):
            if run('git','rev-parse',ref).stdout.strip()!=BASELINE:
                raise SystemExit(ref+' mismatch')
    if run('git','rev-parse','refs/tags/v1.3.0^{}').stdout.strip()!=TAG_TARGET:
        raise SystemExit('stable tag target changed')
    allowlist='release/v1.4.0/tools/patch_wp6_allowlist.py' if integrated else 'release/v1.4.0/tools/patch_wp6_build_spec_allowlist.py'
    run('python',allowlist,'--check')

def main() -> int:
    p=argparse.ArgumentParser(); p.add_argument('--package-only',action='store_true'); p.add_argument('--integrated',action='store_true'); a=p.parse_args()
    validate_plan(); git_checks(a.package_only,a.integrated)
    print(json.dumps({'artifact':'V0_OSAP_GATE3_CLUSTER_B_WP6_BUILD_SPEC','status':'PASS','implementation_authorization':'PENDING_BUILD_SPEC_REVIEW','gate3_closed':False,'release_authorized':False},indent=2,sort_keys=True))
    return 0
if __name__=='__main__':
    raise SystemExit(main())
