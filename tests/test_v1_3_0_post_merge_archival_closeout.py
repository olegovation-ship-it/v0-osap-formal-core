import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
REC=ROOT/"release/v1.3.0/V1_3_0_POST_MERGE_ARCHIVAL_CLOSEOUT_AND_DEVELOPMENT_BRANCH_SYNCHRONIZATION_RECORD.json"
def test_sync_record():
 r=json.loads(REC.read_text()); m=r["merge_closeout"]
 assert m["pull_request"]==18 and m["successful_checks"]==36
 assert m["post_merge_main_head"]==m["post_merge_development_head"]=="53dcd231aa7d5208a2360d737f01bc2e95e9450b"
def test_release_immutable():
 r=json.loads(REC.read_text())
 assert r["release_state"]["stable_tag_peeled_target"]=="13bf095688bcabd5b090f188e9bd28a16237edeb"
 assert r["release_state"]["zenodo_version_doi"]=="10.5281/zenodo.21346728"
 assert all(v is False for v in r["non_actions"].values())
