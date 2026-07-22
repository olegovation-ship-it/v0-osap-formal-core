#!/usr/bin/env python3
"""Validate and canonicalize the recorded WP2 hosted-CI evidence."""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "release/v1.4.0/GATE3_CLUSTER_B_WP2_POST_MERGE_HOSTED_CI_EVIDENCE.json"

def canonical_sha(payload: dict) -> str:
    cp = json.loads(json.dumps(payload))
    cp["canonical_sha256"] = None
    return hashlib.sha256(json.dumps(cp, sort_keys=True, separators=(",", ":")).encode()).hexdigest()

def main() -> int:
    ap=argparse.ArgumentParser(); ap.add_argument("--check",action="store_true"); ns=ap.parse_args()
    payload=json.loads(PATH.read_text(encoding="utf-8")); expected=canonical_sha(payload)
    stale=payload.get("canonical_sha256") != expected
    if not ns.check:
        payload["canonical_sha256"]=expected
        PATH.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n",encoding="utf-8")
        stale=False
    print(json.dumps({"status":"FAIL" if stale else "PASS","canonical_sha256":expected},indent=2,sort_keys=True))
    return 1 if stale else 0
if __name__=="__main__": raise SystemExit(main())
