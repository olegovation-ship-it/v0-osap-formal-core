from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SNAP="7b38ddd6cb9bcfdc7c5713ba73a2c45d6513fbb8"
def test_post_zenodo_replay_layer_present():
    b=(ROOT/"scripts/build_v1_3_0_final_release_evidence_closure_manifest.py").read_text()
    v=(ROOT/"scripts/verify_v1_3_0_final_release_evidence_closure.py").read_text()
    assert SNAP in b and SNAP in v
    assert "ZENODO_PUBLICATION_EVIDENCE_CLOSED" in v

def test_rc1_accepts_successor_markers():
    t=(ROOT/"scripts/verify_rc1_gate_audit.py").read_text()
    assert "ZENODO_PUBLICATION_EVIDENCE_CLOSED" in t and "DOI_FINALIZED" in t
