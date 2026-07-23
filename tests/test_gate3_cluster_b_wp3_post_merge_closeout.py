from __future__ import annotations
import importlib.util, json, subprocess, sys
from pathlib import Path
import pytest
ROOT=Path(__file__).resolve().parents[1]; MERGE='3a3100d88772f3613192db200918d392885a3961'
def module(name,rel):
 s=importlib.util.spec_from_file_location(name,ROOT/rel); m=importlib.util.module_from_spec(s); assert s.loader is not None; s.loader.exec_module(m); return m
def test_wp3_post_merge_records_and_successor_ledger_validate():
 v=module('wp3_pm','scripts/verify_gate3_cluster_b_wp3_post_merge_closeout.py'); assert v.validate_records()==[]; assert v.verify_ledger()==[]
def test_wp3_post_merge_builder_ledger_is_current():
 cp=subprocess.run([sys.executable,'scripts/build_gate3_cluster_b_wp3_post_merge_closeout.py','--check'],cwd=ROOT,text=True,capture_output=True); assert cp.returncode==0,cp.stdout+cp.stderr
def test_canonical_wp3_ledger_remains_byte_exact_at_merge():
 rev=f'{MERGE}:release/v1.4.0/GATE3_CLUSTER_B_WP3_SHA256SUMS.txt'; available=subprocess.run(['git','cat-file','-e',rev],cwd=ROOT,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL).returncode==0
 if not available: pytest.skip('shallow checkout omits exact WP3 merge baseline')
 expected=subprocess.run(['git','show',rev],cwd=ROOT,stdout=subprocess.PIPE,check=True).stdout; assert (ROOT/'release/v1.4.0/GATE3_CLUSTER_B_WP3_SHA256SUMS.txt').read_bytes()==expected
def test_wp3_closeout_has_no_release_or_wp4_authorization():
 c=json.loads((ROOT/'release/v1.4.0/GATE3_CLUSTER_B_WP3_POST_MERGE_ARCHIVAL_CLOSEOUT_RECORD.json').read_text()); assert all(v is False for v in c['release_actions'].values()); assert c['wp4_proof_completion_authorized'] is False; assert c['proof_or_new_runtime_semantics_added'] is False
