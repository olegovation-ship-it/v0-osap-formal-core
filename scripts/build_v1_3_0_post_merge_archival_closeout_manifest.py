from __future__ import annotations
import hashlib, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"release/v1.3.0/V1_3_0_POST_MERGE_ARCHIVAL_CLOSEOUT_AND_DEVELOPMENT_BRANCH_SYNCHRONIZATION_MANIFEST.json"
FILES=[
 ".github/workflows/v1-3-0-post-merge-archival-closeout.yml","CHANGELOG.md","README.md","docs/status_and_nonclaims.md",
 "release/v1.3.0/V1_3_0_POST_MERGE_ARCHIVAL_CLOSEOUT_AND_DEVELOPMENT_BRANCH_SYNCHRONIZATION_ACCEPTANCE_GATES.md",
 "release/v1.3.0/V1_3_0_POST_MERGE_ARCHIVAL_CLOSEOUT_AND_DEVELOPMENT_BRANCH_SYNCHRONIZATION_RECORD.json",
 "release/v1.3.0/V1_3_0_POST_MERGE_ARCHIVAL_CLOSEOUT_AND_DEVELOPMENT_BRANCH_SYNCHRONIZATION_REPORT.md",
 "scripts/build_v1_3_0_post_merge_archival_closeout_manifest.py","scripts/verify_v1_3_0_post_merge_archival_closeout.py",
 "tests/test_v1_3_0_post_merge_archival_closeout.py"]
def main():
 payload={"artifact_id":"V0_OSAP_V1_3_0_POST_MERGE_ARCHIVAL_CLOSEOUT_AND_DEVELOPMENT_BRANCH_SYNCHRONIZATION_MANIFEST",
  "version":"0.1","date":"2026-07-15",
  "state":"POST_MERGE_ARCHIVAL_CLOSEOUT_RECORDED_MAIN_DEVELOPMENT_SYNCHRONIZED_ZENODO_LIFECYCLE_REPLAY_COMPATIBLE_RELEASE_IMMUTABLE",
  "baseline_merge_commit":"53dcd231aa7d5208a2360d737f01bc2e95e9450b",
  "stable_tag_target":"13bf095688bcabd5b090f188e9bd28a16237edeb",
  "zenodo_version_doi":"10.5281/zenodo.21346728",
  "files":{rel:hashlib.sha256((ROOT/rel).read_bytes()).hexdigest() for rel in sorted(FILES)}}
 OUT.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n",encoding="utf-8",newline="\n")
 print(f"PASS: archival-closeout manifest generated with {len(FILES)} hashed files.")
if __name__=="__main__": main()
