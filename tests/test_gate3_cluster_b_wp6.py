from __future__ import annotations
import json, subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def run(*a):
 return subprocess.run(a,cwd=ROOT,capture_output=True,text=True,check=False)
def test_wp6_builder_is_deterministic():
 assert run(sys.executable,'scripts/build_gate3_cluster_b_wp6.py','--check').returncode==0
def test_wp6_full_verifier():
 cp=run(sys.executable,'scripts/verify_gate3_cluster_b_wp6.py','--job','full'); assert cp.returncode==0,cp.stdout+cp.stderr
def test_wp6_fixture_campaign():
 paths=sorted((ROOT/'fixtures/gate3/cluster_b/wp6').glob('*.json')); assert len(paths)==14
 rows=[json.loads(p.read_text()) for p in paths]
 assert rows[0]['expected_disposition']=='ELIGIBLE_FOR_CLOSE_GATE3_PENDING_EXPLICIT_AUTHORIZATION'
 assert all(x['expected_disposition']=='HOLD_WITH_EXPLICIT_BLOCKERS' for x in rows[1:13])
 assert rows[13]['expected_disposition']=='REJECT_UNAUTHORIZED_INPUT' and rows[13]['valid_input'] is False
def test_wp6_decision_is_nonoperative_hold():
 d=json.loads((ROOT/'release/v1.4.0/GATE3_CLUSTER_B_WP6_DECISION_CANDIDATE.json').read_text())
 assert d['candidate']=='HOLD_WITH_EXPLICIT_BLOCKERS'; assert not d['gate3_closed']; assert not d['release_authorized']
