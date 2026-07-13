from __future__ import annotations

import argparse
import os
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path

from rc1_release_closure_lib import read_json, repository_root, sha256_file, write_json

ROOT = repository_root()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--status", choices=["PASS"], required=True)
    parser.add_argument(
        "--output",
        default="artifacts/rc1_clean_room_replay_evidence.json",
    )
    args = parser.parse_args()

    output = ROOT / args.output
    head = os.environ.get("GITHUB_SHA")
    if not head:
        import subprocess
        head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()

    payload = {
        "artifact_id": "V0_OSAP_V1_3_0_RC1_CLEAN_ROOM_REPLAY_EVIDENCE",
        "schema_version": "0.1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": args.status,
        "operator": "github-actions" if os.environ.get("GITHUB_ACTIONS") == "true" else "local-clean-runner",
        "candidate_commit": head,
        "github_run_id": os.environ.get("GITHUB_RUN_ID"),
        "github_run_attempt": os.environ.get("GITHUB_RUN_ATTEMPT"),
        "github_ref": os.environ.get("GITHUB_REF"),
        "runner_os": os.environ.get("RUNNER_OS", platform.system()),
        "platform": platform.platform(),
        "python_version": sys.version.split()[0],
        "hashes": {
            "audit_manifest_sha256": sha256_file(ROOT / "release/v1.3.0/RC1_RELEASE_MANIFEST.json"),
            "closure_manifest_sha256": sha256_file(ROOT / "release/v1.3.0/RC1_RELEASE_CLOSURE_MANIFEST.json"),
            "theorem_inventory_sha256": sha256_file(ROOT / "release/v1.3.0/RC1_THEOREM_INVENTORY.json"),
            "statement_parity_sha256": sha256_file(ROOT / "release/v1.3.0/RC1_STATEMENT_PARITY_EVIDENCE.json"),
        },
        "closure_manifest_state": read_json(ROOT / "release/v1.3.0/RC1_RELEASE_CLOSURE_MANIFEST.json")["state"],
        "release_actions_executed": False,
    }
    write_json(output, payload)
    print(f"PASS: clean-room replay evidence written to {output.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
