from __future__ import annotations
import copy, hashlib, importlib.util, json
from pathlib import Path
import pytest
ROOT=Path(__file__).resolve().parents[1]
def load_mod():
 p=ROOT/'checker/v0_osap_fc1/cluster_b_wp3.py'; s=importlib.util.spec_from_file_location('wp3',p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
M=load_mod()
def load(rel): return json.loads((ROOT/rel).read_text())
def source_hash(x): return hashlib.sha256((json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False)+'\n').encode()).hexdigest()
def bind_fixture(name):
 fx=load('fixtures/gate3/cluster_b/wp3/'+name); return fx,M.bind_wp2_result(fx['source_result'],fx['evidence_lineage'])
def test_all_fixtures_replay():
 man=load('release/v1.4.0/GATE3_CLUSTER_B_WP3_FIXTURE_MANIFEST.json')
 for e in man['fixtures']:
  fx=load(e['path']); out=M.bind_wp2_result(fx['source_result'],fx['evidence_lineage'])
  for k,v in fx['expected'].items(): assert out[k]==v
  assert out['diagnostic_transport']==fx['source_result']['diagnostics']
def test_deterministic_binding():
 fx=load('fixtures/gate3/cluster_b/wp3/02_dle_transition_reject.json')
 assert M.bind_wp2_result(fx['source_result'],fx['evidence_lineage'])==M.bind_wp2_result(fx['source_result'],fx['evidence_lineage'])
def test_evidence_hash_mismatch_rejected():
 fx=load('fixtures/gate3/cluster_b/wp3/01_dle_transition_pass.json'); ev=copy.deepcopy(fx['evidence_lineage']); ev[0]['sha256']='0'*64
 with pytest.raises(M.BindingError): M.bind_wp2_result(fx['source_result'],ev)
def test_exact_case_profile_enforced():
 fx=load('fixtures/gate3/cluster_b/wp3/03_strong_dle_pass.json'); src=copy.deepcopy(fx['source_result']); src['role_ids']=['CB-R2']; ev=copy.deepcopy(fx['evidence_lineage']); ev[0]['sha256']=source_hash(src)
 with pytest.raises(M.BindingError): M.bind_wp2_result(src,ev)
def test_pass_is_not_certified_before_wp4():
 _,out=bind_fixture('01_dle_transition_pass.json'); assert out['candidate_outcome_code']=='CERTIFIED'; assert out['typed_outcome_code']=='INCONCLUSIVE_UNSUPPORTED_FRAGMENT'; assert out['certification_claimed'] is False
def test_inherited_rejections_are_bound():
 _,dle=bind_fixture('02_dle_transition_reject.json'); _,branch=bind_fixture('12_branch_firewall_reject.json'); _,robust=bind_fixture('13_robust_obstruction_reject.json')
 assert dle['typed_outcome_code']=='REJECTED_DLE_FAILURE'; assert branch['typed_outcome_code']=='REJECTED_BRANCH_PROMOTION'; assert robust['typed_outcome_code']=='REJECTED_NONELIM_OBSTRUCTION'
def test_extension_rejection_is_deferred():
 _,out=bind_fixture('08_model_pair_reject.json'); assert out['candidate_outcome_code']=='REJECTED_NONELIM_OBSTRUCTION'; assert out['typed_outcome_code']=='INCONCLUSIVE_UNSUPPORTED_FRAGMENT'; assert out['outcome_binding_status']=='DEFERRED_TO_WP4_PROOF_ACTIVATION'
def test_exact_ipec_vocabulary():
 p=load('release/v1.4.0/GATE3_CLUSTER_B_WP3_IPEC_V0_1_COMPATIBILITY_PROFILE.json')
 assert p['precedence']==['BACKEND_PARITY_FAILURE','REJECTED_BRANCH_PROMOTION','REJECTED_NONELIM_OBSTRUCTION','REJECTED_LIVE_RESIDUAL','REJECTED_DLE_FAILURE','REJECTED_GUARD_FAILURE','INCONCLUSIVE_UNSUPPORTED_FRAGMENT','CERTIFIED']


def test_bounded_wp2_successor_firewall_handoff_is_recorded():
    lock=load('release/v1.4.0/GATE3_CLUSTER_B_WP3_BASELINE_LOCK.json')
    firewall=load('release/v1.4.0/GATE3_CLUSTER_B_WP3_PRESERVATION_FIREWALL.json')
    expected=['scripts/verify_gate3_cluster_b_wp2.py','scripts/verify_gate3_cluster_b_wp2_post_merge_closeout.py','release/v1.4.0/GATE3_CLUSTER_B_WP2_POST_MERGE_SHA256SUMS.txt']
    assert lock['new_file_only'] is False
    assert lock['authorized_modified_paths']==expected
    assert firewall['tracked_modification_authorized'] is True
    assert firewall['authorized_modified_paths']==expected
    assert firewall['canonical_records_modification_authorized'] is False
    assert firewall['canonical_ledgers_modification_authorized'] is False

def test_wp2_verifier_contains_exact_wp3_successor_marker():
    text=(ROOT/'scripts/verify_gate3_cluster_b_wp2.py').read_text(encoding='utf-8')
    assert text.count('WP3_SUCCESSOR_FIREWALL_HANDOFF_V0_1')==2
    assert '"fixtures/gate3/cluster_b/wp3/"' in text
    assert '"release/v1.4.0/GATE3_CLUSTER_B_WP3_"' in text
