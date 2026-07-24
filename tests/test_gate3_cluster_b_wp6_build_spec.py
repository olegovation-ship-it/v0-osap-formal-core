from __future__ import annotations
import json
from pathlib import Path
from jsonschema import Draft202012Validator

ROOT=Path(__file__).resolve().parents[1]

def test_wp6_build_plan_schema_scope_and_cardinalities():
    plan=json.loads((ROOT/'release/v1.4.0/GATE3_CLUSTER_B_WP6_BUILD_PLAN.json').read_text())
    schema=json.loads((ROOT/'schemas/v1.4.0/gate3_cluster_b_wp6_build_plan.schema.json').read_text())
    Draft202012Validator(schema).validate(plan)
    assert plan['new_theorem_ids']==[]
    assert plan['implementation_changed_path_count']==54
    assert plan['build_spec_changed_path_count']==6
    assert plan['ci_job_count']==10
    assert plan['audit_fixture_count']==14
    assert plan['acceptance_gate_count']==24
    assert plan['release_authorization']=='NONE'
    assert plan['gate3_close_authorization']=='NONE'
    assert plan['decision_candidate_values']==[
        'ELIGIBLE_FOR_CLOSE_GATE3_PENDING_EXPLICIT_AUTHORIZATION',
        'HOLD_WITH_EXPLICIT_BLOCKERS',
    ]
