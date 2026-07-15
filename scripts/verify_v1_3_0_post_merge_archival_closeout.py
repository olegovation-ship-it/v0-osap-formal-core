from __future__ import annotations
import argparse, hashlib, json, subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BASE="53dcd231aa7d5208a2360d737f01bc2e95e9450b"
TAG="13bf095688bcabd5b090f188e9bd28a16237edeb"
DOI="10.5281/zenodo.21346728"
REC=ROOT/"release/v1.3.0/V1_3_0_POST_MERGE_ARCHIVAL_CLOSEOUT_AND_DEVELOPMENT_BRANCH_SYNCHRONIZATION_RECORD.json"
MAN=ROOT/"release/v1.3.0/V1_3_0_POST_MERGE_ARCHIVAL_CLOSEOUT_AND_DEVELOPMENT_BRANCH_SYNCHRONIZATION_MANIFEST.json"
def run(*a,check=True): return subprocess.run(list(a),cwd=ROOT,text=True,capture_output=True,check=check)
def exists(ref): return run("git","rev-parse","--verify","--quiet",ref,check=False).returncode==0
def ancestor(a,b): return run("git","merge-base","--is-ancestor",a,b,check=False).returncode==0
def main():
 p=argparse.ArgumentParser(); p.add_argument("--require-tags",action="store_true"); p.add_argument("--require-remote-sync",action="store_true"); n=p.parse_args()
 r=json.loads(REC.read_text()); m=json.loads(MAN.read_text())
 assert r["merge_closeout"]["merge_commit"]==BASE and r["merge_closeout"]["successful_checks"]==36
 assert r["release_state"]["stable_tag_peeled_target"]==TAG and r["release_state"]["zenodo_version_doi"]==DOI
 assert all(v is False for v in r["non_actions"].values())
 for rel,expected in m["files"].items(): assert hashlib.sha256((ROOT/rel).read_bytes()).hexdigest()==expected, rel
 assert ancestor(BASE,"HEAD")
 if n.require_tags: assert exists("refs/tags/v1.3.0") and run("git","rev-parse","v1.3.0^{}").stdout.strip()==TAG
 if n.require_remote_sync:
  for ref in ("refs/remotes/origin/main","refs/remotes/origin/v1.3.0-development"):
   assert exists(ref) and ancestor(BASE,ref), ref
 for rel in ("README.md","CHANGELOG.md","docs/status_and_nonclaims.md"):
  t=(ROOT/rel).read_text(); assert "POST_MERGE_ARCHIVAL_CLOSEOUT_RECORDED" in t and BASE in t and DOI in t
 print("PASS: post-merge archival closeout verified; synchronization baseline preserved and release objects immutable.")
if __name__=="__main__": main()
