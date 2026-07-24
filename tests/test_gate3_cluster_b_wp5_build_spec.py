from __future__ import annotations
import json
from pathlib import Path
from jsonschema import Draft202012Validator
ROOT=Path(__file__).resolve().parents[1]
def test_wp5_build_plan_schema_and_scope():
    plan=json.loads((ROOT/'release/v1.4.0/GATE3_CLUSTER_B_WP5_BUILD_PLAN.json').read_text())
    schema=json.loads((ROOT/'schemas/v1.4.0/gate3_cluster_b_wp5_build_plan.schema.json').read_text())
    Draft202012Validator(schema).validate(plan)
    assert plan['new_theorem_ids']==[]
    assert plan['ci_job_count']==14
    assert plan['acceptance_gate_count']==24
    assert plan['release_authorization']=='NONE'
    assert plan['wp6_authorization']=='NONE'
