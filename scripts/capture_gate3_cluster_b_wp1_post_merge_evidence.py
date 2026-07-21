#!/usr/bin/env python3
"""Canonicalize WP1 closeout evidence and optionally verify PR identity live."""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "release/v1.4.0/GATE3_CLUSTER_B_WP1_POST_MERGE_HOSTED_CI_EVIDENCE.json"
REPO = "olegovation-ship-it/v0-osap-formal-core"


def canonical_sha(payload: dict) -> str:
    cp = json.loads(json.dumps(payload))
    cp["canonical_sha256"] = None
    return hashlib.sha256(json.dumps(cp, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def verify_live() -> None:
    if shutil.which("gh") is None:
        raise SystemExit("ERROR: gh CLI unavailable")
    raw = subprocess.check_output(["gh","pr","view","22","--repo",REPO,"--json","state,mergedAt,mergeCommit,headRefOid"], text=True)
    pr = json.loads(raw)
    assert pr["state"] == "MERGED", pr
    assert pr["headRefOid"] == "8229685e4852f81d9bd2fc20ceec57bf1c7e91e5", pr
    assert pr["mergeCommit"]["oid"] == "eaf142089230ea5a5096ae834bf4e733d5f369aa", pr
    print("LIVE_PR_IDENTITY=PASS")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--verify-live", action="store_true")
    args = parser.parse_args()
    payload = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    expected = canonical_sha(payload)
    if args.verify_live: verify_live()
    if args.check:
        ok = payload.get("canonical_sha256") == expected
        print(json.dumps({"status":"PASS" if ok else "FAIL","canonical_sha256":expected}, indent=2))
        return 0 if ok else 1
    payload["canonical_sha256"] = expected
    EVIDENCE.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status":"PASS","canonical_sha256":expected}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
