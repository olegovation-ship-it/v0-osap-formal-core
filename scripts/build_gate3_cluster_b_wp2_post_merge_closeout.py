#!/usr/bin/env python3
"""Build deterministic WP2 post-merge closeout SHA-256 successor ledger."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "release/v1.4.0/GATE3_CLUSTER_B_WP2_POST_MERGE_SHA256SUMS.txt"
LEDGER_INPUTS = ['.github/workflows/gate3-cluster-b-wp2-post-merge-closeout.yml', 'docs/gate3/cluster_b/WP2_POST_MERGE_ARCHIVAL_CLOSEOUT_AND_DEVELOPMENT_BRANCH_SYNCHRONIZATION.md', 'release/v1.4.0/GATE3_CLUSTER_B_WP2_DEVELOPMENT_BRANCH_SYNCHRONIZATION_RECORD.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP2_POST_MERGE_ARCHIVAL_CLOSEOUT_RECORD.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP2_POST_MERGE_CLOSEOUT_GATES.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP2_POST_MERGE_FROZEN_UPSTREAM_PRESERVATION_RECORD.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP2_POST_MERGE_HOSTED_CI_EVIDENCE.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP2_POST_MERGE_SCHEMA_BUNDLE_MANIFEST.json', 'release/v1.4.0/tools/patch_wp2_post_merge_allowlist.py', 'schemas/v1.4.0/gate3_cluster_b_wp2_development_branch_synchronization_record.schema.json', 'schemas/v1.4.0/gate3_cluster_b_wp2_post_merge_archival_closeout_record.schema.json', 'schemas/v1.4.0/gate3_cluster_b_wp2_post_merge_closeout_gates.schema.json', 'schemas/v1.4.0/gate3_cluster_b_wp2_post_merge_frozen_upstream_preservation_record.schema.json', 'schemas/v1.4.0/gate3_cluster_b_wp2_post_merge_hosted_ci_evidence.schema.json', 'scripts/build_gate3_cluster_b_wp2.py', 'scripts/build_gate3_cluster_b_wp2_post_merge_closeout.py', 'scripts/capture_gate3_cluster_b_wp2_post_merge_evidence.py', 'scripts/synchronize_v1_4_0_development_wp2.sh', 'scripts/verify_gate3_cluster_b_wp2.py', 'scripts/verify_gate3_cluster_b_wp2_post_merge_closeout.py', 'tests/test_gate3_cluster_b_wp2_post_merge_closeout.py']
VERIFY = ROOT / "scripts/verify_gate3_cluster_b_wp2_post_merge_closeout.py"


REPAIR_BASE = "ba32d8e855a79461fdcda14740acab86aafcb17a"
REPAIR_STEM = (
    "GATE3_CLUSTER_B_WP6_POST_MERGE_PUSH_CONTEXT_COMPATIBILITY_"
    "AND_PREDECESSOR_WORKFLOW_ISOLATION_REPAIR"
)
REPAIR_MANIFEST = (
    ROOT / f"release/v1.4.0/{REPAIR_STEM}_MANIFEST.json"
)


def parse_ledger(value: str) -> dict[str, str]:
    entries: dict[str, str] = {}

    for line in value.splitlines():
        if line.strip():
            digest, relative = line.split("  ", 1)
            entries[relative] = digest

    return entries


def repair_overlay_attestation(
) -> tuple[dict[str, str], dict[str, str]] | None:
    try:
        manifest = json.loads(
            REPAIR_MANIFEST.read_text(encoding="utf-8")
        )

        if manifest.get("baseline_commit") != REPAIR_BASE:
            return None

        ledger_rel = manifest["ledger_path"]
        repair = parse_ledger(
            (ROOT / ledger_rel).read_text(encoding="utf-8")
        )

        surface = set(
            manifest["controlled_modified_paths"]
            + manifest["additive_paths"]
        )
        ledger_inputs = surface - {ledger_rel}

        if set(repair) != ledger_inputs:
            return None

        status = subprocess.run(
            [
                "git",
                "status",
                "--porcelain=v1",
                "--untracked-files=all",
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

        if status.returncode:
            return None

        actual_surface = {
            line[3:]
            for line in status.stdout.splitlines()
            if line
        }

        if actual_surface != surface:
            return None

        for relative, expected in repair.items():
            target = ROOT / relative

            if not target.is_file():
                return None

            actual = hashlib.sha256(
                target.read_bytes()
            ).hexdigest()

            if actual != expected:
                return None

        ledger_rel = LEDGER.relative_to(ROOT).as_posix()
        frozen = subprocess.run(
            ["git", "show", f"{REPAIR_BASE}:{ledger_rel}"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

        if frozen.returncode:
            return None

        return repair, parse_ledger(frozen.stdout)

    except Exception:
        return None


def expected_ledger() -> str:
    attestation = repair_overlay_attestation()
    rows: list[str] = []

    for rel in LEDGER_INPUTS:
        target = ROOT / rel

        if not target.is_file():
            raise SystemExit(
                f"ERROR: closeout path missing: {rel}"
            )

        current = hashlib.sha256(
            target.read_bytes()
        ).hexdigest()
        selected = current

        if attestation is not None:
            repair, frozen = attestation

            if repair.get(rel) == current:
                if rel not in frozen:
                    raise SystemExit(
                        "ERROR: repair-attested WP2 path absent "
                        f"from frozen successor ledger: {rel}"
                    )

                selected = frozen[rel]

        rows.append(f"{selected}  {rel}")

    return "\n".join(rows) + "\n"


def load_verifier():
    spec = importlib.util.spec_from_file_location("wp2_post_merge_verify", VERIFY)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    expected = expected_ledger()
    stale = not LEDGER.is_file() or LEDGER.read_text(encoding="utf-8") != expected
    if args.check:
        print(json.dumps({"status":"FAIL" if stale else "PASS","stale":[LEDGER.relative_to(ROOT).as_posix()] if stale else []}, indent=2, sort_keys=True))
        return 1 if stale else 0
    LEDGER.write_text(expected, encoding="utf-8")
    verifier = load_verifier()
    errors = verifier.validate_records() + verifier.verify_ledger()
    print(json.dumps({"status":"PASS" if not errors else "FAIL","decision":"READY_FOR_HOSTED_CI" if not errors else "HOLD_WITH_BLOCKERS","errors":errors}, indent=2, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
