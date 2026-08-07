#!/usr/bin/env python3
"""Deterministically build/check the v1.4.0 final-release evidence closure manifest."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

BASE_COMMIT = "75b84e5800686372fb6a19add12c8896f59274ee"
BASE_TREE = "8ec377cadaeddfd6bef67dd01d981b83d09c327b"
BASE_PARENTS = ["47614ce7891f4895e003cb85e7651b7d043a963d","aeeaeefa5d40bbb26ffe7c9ae02abc75b3636a5d"]
BASE_RELEASE_TREE = "45aaeec48443924fa153ac343ab904bac814792f"
MANIFEST_PATH = "release/v1.4.0/V1_4_0_FINAL_RELEASE_EVIDENCE_CLOSURE_MANIFEST.json"
EXACT_SURFACE = [
    "README.md","CHANGELOG.md","docs/status_and_nonclaims.md",
    "artifacts/v1_4_0_github_final_release_evidence.json",
    "release/v1.4.0/V1_4_0_GITHUB_FINAL_RELEASE_EVIDENCE.json",
    "release/v1.4.0/V1_4_0_FINAL_RELEASE_EVIDENCE_CLOSURE_RECORD.json",
    MANIFEST_PATH,
    "release/v1.4.0/V1_4_0_FINAL_RELEASE_EVIDENCE_CLOSURE_AND_HISTORICAL_PRESERVATION_REPORT.md",
    "release/v1.4.0/V1_4_0_FINAL_RELEASE_EVIDENCE_CLOSURE_ACCEPTANCE_GATES.md",
    "scripts/build_v1_4_0_final_release_evidence_closure_manifest.py",
    "scripts/verify_v1_4_0_final_release_evidence_closure.py",
    "tests/test_v1_4_0_final_release_evidence_closure.py",
    ".github/workflows/v1-4-0-final-release-evidence-closure.yml",
]
MODIFIED = EXACT_SURFACE[:3]
ADDITIVE = EXACT_SURFACE[3:]
BASELINE_MODIFIED = {
    "README.md":{"byte_count":10923,"sha256":"ac33412cb23ca1a44b1822ba343678076883582457e16e3597d8db6925b8447d","git_blob_sha1":"77e00ab3a6de603769e8bd8603cf8b0bd3e8ee57"},
    "CHANGELOG.md":{"byte_count":9839,"sha256":"dfa17a0ed02d0552295a1b4e3382e92cc8e70a18b158c2861525e8a70b60256c","git_blob_sha1":"1be8f7cba66d507e69cb73a42e304e75d7e3eea0"},
    "docs/status_and_nonclaims.md":{"byte_count":8901,"sha256":"49cc49f733ac7d53787d3df2a7c606cc18e0872c48290c51583e526010092a1d","git_blob_sha1":"a8cf9f4806ce8155bf9735d4d58d01c207edbbe0"},
}

def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def git_blob_sha1(data: bytes) -> str:
    return hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest()

def canonical_json_bytes(obj: object) -> bytes:
    return (json.dumps(obj, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")

def build_manifest(root: Path) -> dict:
    files=[]
    for rel in EXACT_SURFACE:
        if rel == MANIFEST_PATH:
            continue
        data=(root/rel).read_bytes()
        files.append({"path":rel,"classification":"MODIFIED" if rel in MODIFIED else "ADDITIVE",
                      "byte_count":len(data),"sha256":sha256_bytes(data),"git_blob_sha1":git_blob_sha1(data)})
    return {
      "artifact_id":"V0_OSAP_V1_4_0_FINAL_RELEASE_EVIDENCE_CLOSURE_MANIFEST","version":"1.0","date":"2026-08-07",
      "state":"FINAL_RELEASE_EVIDENCE_CLOSED / STABLE_TAG_CREATED / FINAL_GITHUB_RELEASE_CREATED / ZENODO_NOT_PUBLISHED",
      "baseline":{"commit":BASE_COMMIT,"tree":BASE_TREE,"parents":BASE_PARENTS,"release_v1_4_0_subtree":BASE_RELEASE_TREE,
                  "modified_path_identities":BASELINE_MODIFIED,
                  "citation_cff_blob_sha1":"0adb7aaa73a052b8621c3f0d393f6f128cf4bada",
                  "pyproject_blob_sha1":"8e2b30975f15d4147aabb7a50fe8bab3b9ea65a8"},
      "surface":{"modified":MODIFIED,"additive":ADDITIVE,"modified_count":3,"additive_count":10,"total_count":13,"removals":[]},
      "manifest_self_exclusion":{"path":MANIFEST_PATH,"reason":"Avoid circular self-hash; outer package manifest hashes all 13 payload files including this manifest."},
      "files_excluding_self":files,
      "historical_preservation":{"baseline_release_v1_4_0_tree_sha1":BASE_RELEASE_TREE,"require_all_preexisting_paths_byte_identical":True,
                                 "historical_wp6_classification":"HISTORICAL_PRE_PR34_NON_TERMINAL_EVIDENCE"},
      "release_freeze":{"tag_object_sha1":"21d9a42ceb9985dbcd6330582a8cb80e81d883c5","tag_peeled_target":BASE_COMMIT,
                        "tag_message_sha256":"9dbffe6f0bf3182f9e19fe278d8b3834ed3bb607d75282bae814db39b8fee5a5",
                        "release_id":366706025,"release_body_sha256":"530711e7baa7408f51f53844c969020520a0c0bd5c100bfe29275867735623ba","release_asset_count":4},
      "publication_boundary":{"zenodo_v1_4_0_created":False,"v1_4_0_doi_finalized":False,"doi_mutation_performed":False},
      "component_version_boundary":{"repository_release":"v1.4.0","checker_project":"0.7.0.dev1","separate_namespaces":True},
    }

def render_manifest(root: Path) -> bytes:
    return canonical_json_bytes(build_manifest(root))

def main() -> int:
    ap=argparse.ArgumentParser()
    ap.add_argument("--root",type=Path,default=Path(__file__).resolve().parents[1])
    mode=ap.add_mutually_exclusive_group()
    mode.add_argument("--check",action="store_true")
    mode.add_argument("--write",action="store_true")
    args=ap.parse_args(); root=args.root.resolve(); expected=render_manifest(root); target=root/MANIFEST_PATH
    if args.write:
        target.parent.mkdir(parents=True,exist_ok=True); target.write_bytes(expected)
        print(f"MANIFEST_WRITE=PASS bytes={len(expected)} sha256={sha256_bytes(expected)}"); return 0
    if not target.is_file():
        print("MANIFEST_CHECK=HOLD reason=MANIFEST_MISSING"); return 1
    actual=target.read_bytes()
    if actual != expected:
        print(f"MANIFEST_CHECK=HOLD reason=MANIFEST_MISMATCH expected_sha256={sha256_bytes(expected)} actual_sha256={sha256_bytes(actual)}"); return 1
    print(f"MANIFEST_CHECK=PASS bytes={len(actual)} sha256={sha256_bytes(actual)}"); return 0

if __name__=="__main__":
    raise SystemExit(main())
