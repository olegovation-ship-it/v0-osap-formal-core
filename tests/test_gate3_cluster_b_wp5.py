from __future__ import annotations
import json
import subprocess
import sys
from pathlib import Path
from jsonschema import Draft202012Validator
ROOT=Path(__file__).resolve().parents[1]
def load(rel): return json.loads((ROOT/rel).read_text())
def test_wp5_static_records_and_cardinality():
    assert load('release/v1.4.0/GATE3_CLUSTER_B_WP5_CI_JOB_MATRIX.json')['job_count']==14
    gates=load('release/v1.4.0/GATE3_CLUSTER_B_WP5_ACCEPTANCE_GATES.json')
    assert gates['gate_count']==24 and not gates['close_gate3_authorized']
    plan=load('release/v1.4.0/GATE3_CLUSTER_B_WP5_BUILD_PLAN.json')
    assert plan['new_theorem_ids']==[]
    assert len(plan['semantic_role_ids'])==7

def test_wp5_evidence_control_fixtures():
    manifest=load('release/v1.4.0/GATE3_CLUSTER_B_WP5_FIXTURE_MANIFEST.json')
    assert manifest['fixture_count']==6
    for row in manifest['fixtures']:
        cp=subprocess.run([sys.executable,'scripts/replay_gate3_cluster_b_wp5.py','--fixture',row['path']],cwd=ROOT,capture_output=True,text=True)
        assert cp.returncode==0, cp.stdout+cp.stderr

def test_wp5_replay_record_is_byte_identical():
    rec=load('release/v1.4.0/GATE3_CLUSTER_B_WP5_REPLAY_RECORD.json')
    assert rec['byte_identical'] is True
    assert rec['run_1_sha256']==rec['run_2_sha256']==rec['canonical_bundle_sha256']
