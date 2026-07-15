from __future__ import annotations

import argparse, hashlib, json, subprocess
from v1_3_0_final_release_evidence_closure_lib import (
    EVIDENCE_PATH, EXPECTED_PUBLISHED_AT, EXPECTED_RELEASE_NAME, EXPECTED_RELEASE_URL,
    FINAL_AUTHORIZATION_MERGE_COMMIT, FINAL_TAG, FINAL_TARGET, HUMAN_STATE,
    IMMUTABLE_DOI, IMMUTABLE_TAG, IMMUTABLE_TARGET, MACHINE_STATE, MANIFEST_PATH,
    RC1_TAG, RC1_TARGET, RECORD_PATH, REPOSITORY, remote_tag_map, repository_root,
    run, tag_exists, tag_object_sha, tag_object_type, tag_target,
)
ROOT=repository_root()
HISTORICAL_SNAPSHOT="7b38ddd6cb9bcfdc7c5713ba73a2c45d6513fbb8"
ZENODO_DOI="10.5281/zenodo.21346728"
SUCCESSOR_MARKERS=("ZENODO_PUBLICATION_AUTHORIZED","ZENODO_PUBLICATION_EVIDENCE_CLOSED","DOI_FINALIZED")

def req(c,m):
    if not c: raise SystemExit("historical lifecycle replay failed: "+m)

def blob(rel):
    return subprocess.run(["git","show",f"{HISTORICAL_SNAPSHOT}:{rel}"],cwd=ROOT,check=True,capture_output=True).stdout

def j(rel): return json.loads(blob(rel).decode("utf-8"))
def text(rel): return blob(rel).decode("utf-8")
def sha(rel): return hashlib.sha256(blob(rel)).hexdigest()
def norm(s): return s.replace("\r\n","\n").strip()

def verify(require_tags=False,verify_live=False):
    for commit in (FINAL_AUTHORIZATION_MERGE_COMMIT,HISTORICAL_SNAPSHOT):
        req(run("git","merge-base","--is-ancestor",commit,"HEAD",check=False).returncode==0,f"{commit} not ancestor of HEAD")
    if require_tags:
        for tag,target in ((IMMUTABLE_TAG,IMMUTABLE_TARGET),(RC1_TAG,RC1_TARGET),(FINAL_TAG,FINAL_TARGET)):
            req(tag_exists(tag) and tag_target(tag)==target,f"tag mismatch: {tag}")
    req(tag_object_type(FINAL_TAG)=="tag","stable tag not annotated")
    obj=tag_object_sha(FINAL_TAG); remote=remote_tag_map(FINAL_TAG)
    req(remote.get(f"refs/tags/{FINAL_TAG}") == obj,"remote tag object mismatch")
    req(remote.get(f"refs/tags/{FINAL_TAG}^{{}}") == FINAL_TARGET,"remote peeled target mismatch")

    evidence=j(EVIDENCE_PATH.as_posix()); record=j(RECORD_PATH.as_posix()); manifest=j(MANIFEST_PATH.as_posix())
    for rel in (EVIDENCE_PATH,RECORD_PATH,MANIFEST_PATH):
        p=ROOT/rel; req(p.is_file(),f"missing {rel}")
        req(p.read_bytes()==blob(rel.as_posix()),f"historical artifact mutated: {rel}")
    tag=evidence["stable_tag"]; release=evidence["release"]
    req(tag["tagName"]==FINAL_TAG and tag["peeledTargetCommit"]==FINAL_TARGET,"stable tag evidence mismatch")
    req(release["tagName"]==FINAL_TAG and release["name"]==EXPECTED_RELEASE_NAME,"release identity mismatch")
    req(release["url"]==EXPECTED_RELEASE_URL and release["publishedAt"]==EXPECTED_PUBLISHED_AT,"release metadata mismatch")
    req(release["isDraft"] is False and release["isPrerelease"] is False and release["isLatest"] is True,"release state mismatch")
    notes=norm(text("release/v1.3.0/V1_3_0_GITHUB_FINAL_RELEASE_NOTES.md"))
    req(hashlib.sha256(notes.encode()).hexdigest()==release["normalizedBodySha256"],"historical notes hash mismatch")
    req(record["state"]==MACHINE_STATE and record["human_state"]==HUMAN_STATE,"record state mismatch")
    for rel,expected in record["authorization_basis"]["frozen_historical_artifacts_sha256"].items(): req(sha(rel)==expected,f"frozen predecessor changed: {rel}")
    req(manifest["state"]==MACHINE_STATE and manifest["exact_stable_target"]==FINAL_TARGET,"manifest state mismatch")
    for rel,expected in manifest["files"].items(): req(sha(rel)==expected,f"manifest replay mismatch: {rel}")
    for rel in ("README.md","docs/status_and_nonclaims.md"):
        cur=(ROOT/rel).read_text(encoding="utf-8")
        req(any(x in cur for x in SUCCESSOR_MARKERS),f"successor state absent from {rel}")
        req(ZENODO_DOI in cur and FINAL_TARGET in cur,f"current publication metadata absent from {rel}")
    req('version = "0.7.0.dev1"' in (ROOT/"pyproject.toml").read_text(),"checker version changed")
    req(ZENODO_DOI in (ROOT/"CITATION.cff").read_text(),"current DOI missing from CITATION.cff")
    if verify_live:
        live=json.loads(run("gh","release","view",FINAL_TAG,"--repo",REPOSITORY,"--json","tagName,name,isDraft,isPrerelease,publishedAt,url,targetCommitish,body").stdout)
        req(live["url"]==EXPECTED_RELEASE_URL and live["publishedAt"]==EXPECTED_PUBLISHED_AT,"live release mismatch")
        req(norm(live["body"])==notes,"live release notes differ")
    print(f"PASS: pre-Zenodo final-release evidence replayed from {HISTORICAL_SNAPSHOT}; DOI-finalized successor accepted without predecessor mutation.")

def main():
    p=argparse.ArgumentParser(); p.add_argument("--require-tags",action="store_true"); p.add_argument("--verify-live",action="store_true"); a=p.parse_args(); verify(a.require_tags,a.verify_live); return 0
if __name__=="__main__": raise SystemExit(main())
