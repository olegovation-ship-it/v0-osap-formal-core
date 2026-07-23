#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "release/v1.4.0/GATE3_CLUSTER_B_WP4_POST_MERGE_HOSTED_CI_EVIDENCE.json"

def canonical_sha(obj: dict) -> str:
    copy_obj = json.loads(json.dumps(obj))
    copy_obj["canonical_sha256"] = None
    payload = json.dumps(copy_obj, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.parse_args()

    obj = json.loads(PATH.read_text(encoding="utf-8"))
    errors: list[str] = []
    if obj.get("source_pr") != 27:
        errors.append("source PR mismatch")
    if obj.get("source_head_sha") != "633c01e33271ffb17c045f69aa266a595ebc7e74":
        errors.append("source head mismatch")
    if obj.get("merge_commit") != "cdae3ea4e50f6222182f2398c350476fbe820f92":
        errors.append("merge commit mismatch")
    if obj.get("check_summary") != {
        "success": 25, "failure": 0, "pending": 0, "skipped": 0, "total": 25
    }:
        errors.append("check summary mismatch")
    if obj.get("canonical_sha256") != canonical_sha(obj):
        errors.append("canonical evidence hash mismatch")
    if errors:
        raise SystemExit("; ".join(errors))
    print("WP4 POST-MERGE EVIDENCE CHECK: PASS")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
