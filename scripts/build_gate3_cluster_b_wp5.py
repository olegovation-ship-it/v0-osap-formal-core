#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, subprocess
from pathlib import Path
from jsonschema import Draft202012Validator
ROOT=Path(__file__).resolve().parents[1]
MERGE='adda93cae34d6579e8b715d4107ff7f62a6f9c6b'
CANONICAL=ROOT/'release/v1.4.0/GATE3_CLUSTER_B_WP5_SHA256SUMS.txt'
SUCCESSOR=ROOT/'release/v1.4.0/GATE3_CLUSTER_B_WP5_POST_MERGE_SHA256SUMS.txt'
CONTROLLED=['release/v1.4.0/tools/patch_wp5_allowlist.py', 'scripts/build_gate3_cluster_b_wp5.py', 'scripts/verify_gate3_cluster_b_wp5.py']
PAIRS=[
('release/v1.4.0/GATE3_CLUSTER_B_WP5_BUILD_PLAN.json','schemas/v1.4.0/gate3_cluster_b_wp5_build_plan.schema.json'),
('release/v1.4.0/GATE3_CLUSTER_B_WP5_BASELINE_LOCK.json','schemas/v1.4.0/gate3_cluster_b_wp5_baseline_lock.schema.json'),
('release/v1.4.0/GATE3_CLUSTER_B_WP5_CI_JOB_MATRIX.json','schemas/v1.4.0/gate3_cluster_b_wp5_ci_job_matrix.schema.json'),
('release/v1.4.0/GATE3_CLUSTER_B_WP5_EVIDENCE_INPUT_MANIFEST.json','schemas/v1.4.0/gate3_cluster_b_wp5_evidence_input_manifest.schema.json'),
('release/v1.4.0/GATE3_CLUSTER_B_WP5_FIXTURE_MANIFEST.json','schemas/v1.4.0/gate3_cluster_b_wp5_fixture_manifest.schema.json'),
('release/v1.4.0/GATE3_CLUSTER_B_WP5_PRESERVATION_FIREWALL.json','schemas/v1.4.0/gate3_cluster_b_wp5_preservation_firewall.schema.json'),
('release/v1.4.0/GATE3_CLUSTER_B_WP5_REPLAY_RECORD.json','schemas/v1.4.0/gate3_cluster_b_wp5_replay_record.schema.json'),
('release/v1.4.0/GATE3_CLUSTER_B_WP5_ACCEPTANCE_GATES.json','schemas/v1.4.0/gate3_cluster_b_wp5_acceptance_gates.schema.json'),
('release/v1.4.0/GATE3_CLUSTER_B_WP5_SCHEMA_BUNDLE_MANIFEST.json','schemas/v1.4.0/gate3_cluster_b_wp5_schema_bundle_manifest.schema.json')]
def run(*a,text=True):
    cp=subprocess.run(a,cwd=ROOT,capture_output=True,text=text,check=False)
    if cp.returncode:
        err=cp.stderr if text else cp.stderr.decode('utf-8',errors='replace')
        raise SystemExit(err)
    return cp
def load(r): return json.loads((ROOT/r).read_text(encoding='utf-8'))
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def ledger(p):
    out={}
    for line in p.read_text(encoding='utf-8').splitlines():
        if line.strip():
            h,r=line.split('  ',1); out[r]=h
    return out
def check():
    if CANONICAL.read_bytes()!=run('git','show',f'{MERGE}:release/v1.4.0/GATE3_CLUSTER_B_WP5_SHA256SUMS.txt',text=False).stdout:
        raise SystemExit('canonical WP5 ledger modified')
    old=ledger(CANONICAL); new=ledger(SUCCESSOR)
    if set(old)&set(new)!=set(CONTROLLED): raise SystemExit('unexpected canonical/successor overlap')
    for rel,h in old.items():
        p=ROOT/rel
        if not p.is_file() or digest(p)!=new.get(rel,h): raise SystemExit('WP5 canonical/successor digest mismatch '+rel)
    for rel,h in new.items():
        p=ROOT/rel
        if not p.is_file() or digest(p)!=h: raise SystemExit('WP5 successor digest mismatch '+rel)
    for doc,sch in PAIRS:
        errs=sorted(Draft202012Validator(load(sch)).iter_errors(load(doc)),key=lambda e:list(e.path))
        if errs: raise SystemExit('schema failure '+doc+': '+errs[0].message)
    if load('release/v1.4.0/GATE3_CLUSTER_B_WP5_REPLAY_RECORD.json')['byte_identical'] is not True:
        raise SystemExit('WP5 deterministic replay record failure')
def main():
    p=argparse.ArgumentParser(); p.add_argument('--check',action='store_true'); p.parse_args()
    check(); print('WP5 BUILD: PASS (post-merge successor compatible)'); return 0
if __name__=='__main__': raise SystemExit(main())
