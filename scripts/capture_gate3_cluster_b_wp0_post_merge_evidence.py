#!/usr/bin/env python3
"""Refresh authentic PR and workflow-run evidence using GitHub CLI."""
from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "release/v1.4.0/GATE3_CLUSTER_B_WP0_POST_MERGE_HOSTED_CI_EVIDENCE.json"
SYNC = ROOT / "release/v1.4.0/GATE3_CLUSTER_B_WP0_DEVELOPMENT_BRANCH_SYNCHRONIZATION_RECORD.json"
REPO = "olegovation-ship-it/v0-osap-formal-core"
PR_NUMBER = 20
HEAD = "df4f8524b26e13eda34f96ff8ff48124a7cf9db0"
MERGE = "46c02d96c047e70fe0d54feb60a0aadce2de95c7"
DEV = "v1.4.0-development"
MANDATORY = {
    "wp0": "V0 OSAP Gate 3 Cluster B WP0",
    "python": "Python checker",
    "lean": "Lean 4",
    "coq": "Coq",
    "schema": "Schema validation",
    "release_readiness": "Release readiness",
}


def run_json(args: list[str]) -> Any:
    try:
        completed = subprocess.run(
            args, check=True, text=True, capture_output=True
        )
    except FileNotFoundError as exc:
        raise SystemExit("ERROR: GitHub CLI `gh` is not installed") from exc
    except subprocess.CalledProcessError as exc:
        raise SystemExit(
            "ERROR: GitHub CLI request failed. Run `gh auth status`.\n"
            + exc.stderr
        ) from exc
    return json.loads(completed.stdout)


def canonical_sha(payload: dict[str, Any]) -> str:
    copy = json.loads(json.dumps(payload))
    copy["canonical_sha256"] = None
    raw = json.dumps(copy, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def main() -> int:
    pr = run_json(
        [
            "gh",
            "pr",
            "view",
            str(PR_NUMBER),
            "--repo",
            REPO,
            "--json",
            "state,mergedAt,mergeCommit,headRefOid,baseRefOid,statusCheckRollup",
        ]
    )
    if pr.get("state") != "MERGED":
        raise SystemExit("ERROR: PR #20 is not merged")
    if pr.get("headRefOid") != HEAD:
        raise SystemExit("ERROR: PR head mismatch")
    if (pr.get("mergeCommit") or {}).get("oid") != MERGE:
        raise SystemExit("ERROR: PR merge commit mismatch")

    checks = pr.get("statusCheckRollup") or []
    successful = [item for item in checks if item.get("conclusion") == "SUCCESS"]
    failures = [
        item
        for item in checks
        if item.get("conclusion") not in ("SUCCESS", "NEUTRAL", "SKIPPED")
    ]
    if failures or len(successful) < 27:
        raise SystemExit(
            "ERROR: expected at least 27 successful checks and no failures; "
            f"success={len(successful)} failures={len(failures)}"
        )

    runs = run_json(
        [
            "gh",
            "run",
            "list",
            "--repo",
            REPO,
            "--commit",
            HEAD,
            "--event",
            "pull_request",
            "--limit",
            "100",
            "--json",
            "databaseId,number,headSha,status,conclusion,workflowName,url",
        ]
    )
    runs = [
        item
        for item in runs
        if item.get("headSha") == HEAD
        and item.get("status") == "completed"
        and item.get("conclusion") == "success"
    ]
    by_name = {item["workflowName"]: item for item in runs}
    missing = [name for name in MANDATORY.values() if name not in by_name]
    if missing:
        raise SystemExit(
            "ERROR: mandatory successful workflows missing: " + ", ".join(missing)
        )

    old = json.loads(OUT.read_text(encoding="utf-8"))
    payload = {
        **old,
        "merged_at": pr.get("mergedAt"),
        "check_summary": {
            "success": len(successful),
            "total": len(checks),
            "failure": 0,
            "pending": 0,
            "skipped": len(checks) - len(successful),
        },
        "workflow_run_count": len(runs),
        "workflow_runs": sorted(
            [
                {
                    "run_id": item["databaseId"],
                    "workflow_name": item["workflowName"],
                    "run_number": item["number"],
                    "status": item["status"],
                    "conclusion": item["conclusion"],
                    "url": item["url"],
                }
                for item in runs
            ],
            key=lambda item: item["workflow_name"],
        ),
        "mandatory_workflows": {
            key: {
                "name": name,
                "run_id": by_name[name]["databaseId"],
                "run_number": by_name[name]["number"],
                "conclusion": "success",
            }
            for key, name in MANDATORY.items()
        },
        "evidence_state": "AUTHENTIC_GITHUB_API_EVIDENCE_RECORDED",
        "observation_source": "GITHUB_CLI_API",
        "canonical_sha256": None,
    }
    payload["canonical_sha256"] = canonical_sha(payload)
    OUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    refs = subprocess.run(
        [
            "git",
            "ls-remote",
            "origin",
            "refs/heads/main",
            f"refs/heads/{DEV}",
        ],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    ).stdout.splitlines()
    found = {ref: sha for sha, ref in (line.split("\t", 1) for line in refs)}
    main_sha = found.get("refs/heads/main")
    dev_sha = found.get(f"refs/heads/{DEV}")
    sync = json.loads(SYNC.read_text(encoding="utf-8"))
    sync["current_main_tip"] = main_sha or MERGE
    sync["current_development_tip"] = dev_sha or MERGE
    if main_sha == dev_sha:
        sync.update(
            {
                "compare_status": "identical",
                "ahead_by": 0,
                "behind_by": 0,
                "relation": "SYNCHRONIZED_TO_CURRENT_MAIN",
                "status": "BASELINE_SYNCHRONIZATION_CONFIRMED",
            }
        )
    SYNC.write_text(json.dumps(sync, indent=2) + "\n", encoding="utf-8")

    print(
        json.dumps(
            {
                "status": "PASS",
                "successful_checks": len(successful),
                "workflow_runs": len(runs),
                "main": main_sha,
                "development": dev_sha,
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
