from __future__ import annotations

import argparse
import json
import shlex
import shutil
import subprocess
from pathlib import Path

from rc1_tag_release_lib import (
    CANDIDATE_TAG,
    CLOSURE_MERGE_COMMIT,
    REPOSITORY,
    read_json,
    remote_tag_target,
    repository_root,
)

ROOT = repository_root()
METADATA_PATH = ROOT / "release/v1.3.0/RC1_GITHUB_PRERELEASE_METADATA.json"
EVIDENCE_PATH = ROOT / "artifacts/rc1_github_prerelease_evidence.json"


def fail(message: str) -> None:
    raise SystemExit(f"RC1 GitHub pre-release creation refused: {message}")


def run(command: list[str], check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=check)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Create the authorized GitHub pre-release. Dry-run by default."
    )
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--remote", default="origin")
    parser.add_argument("--confirm-tag")
    args = parser.parse_args()

    metadata = read_json(METADATA_PATH)
    if metadata["tag_name"] != CANDIDATE_TAG or metadata["target_commit"] != CLOSURE_MERGE_COMMIT:
        fail("pre-release metadata is inconsistent")
    if args.execute and args.confirm_tag != CANDIDATE_TAG:
        fail(f"--confirm-tag must equal {CANDIDATE_TAG}")

    remote_target = remote_tag_target(args.remote, CANDIDATE_TAG)
    if remote_target != CLOSURE_MERGE_COMMIT:
        fail(f"remote tag target is {remote_target!r}, expected {CLOSURE_MERGE_COMMIT}")

    if shutil.which("gh") is None:
        fail("GitHub CLI 'gh' is not installed")

    auth = run(["gh", "auth", "status"], check=False)
    if auth.returncode != 0:
        fail("GitHub CLI is not authenticated")

    existing = run(["gh", "release", "view", CANDIDATE_TAG, "--repo", REPOSITORY], check=False)
    if existing.returncode == 0:
        fail(f"a GitHub Release already exists for {CANDIDATE_TAG}")

    command = [
        "gh",
        "release",
        "create",
        CANDIDATE_TAG,
        "--repo",
        REPOSITORY,
        "--title",
        metadata["name"],
        "--notes-file",
        metadata["notes_file"],
        "--prerelease",
        "--verify-tag",
    ]

    if not args.execute:
        print("DRY RUN: no GitHub pre-release was created.")
        print("Authorized command:")
        print("  " + shlex.join(command))
        print(f"Required explicit tag confirmation: {CANDIDATE_TAG}")
        return 0

    created = run(command, check=False)
    if created.returncode != 0:
        fail(created.stderr.strip() or "gh release create failed")

    view = run([
        "gh",
        "release",
        "view",
        CANDIDATE_TAG,
        "--repo",
        REPOSITORY,
        "--json",
        "url,tagName,name,isPrerelease,isDraft,publishedAt",
    ])
    evidence = json.loads(view.stdout)
    if evidence.get("tagName") != CANDIDATE_TAG:
        fail("created release tag mismatch")
    if evidence.get("isPrerelease") is not True or evidence.get("isDraft") is not False:
        fail("created release flags mismatch")

    EVIDENCE_PATH.parent.mkdir(parents=True, exist_ok=True)
    EVIDENCE_PATH.write_text(
        json.dumps(
            {
                "artifact_id": "V0_OSAP_V1_3_0_RC1_GITHUB_PRERELEASE_EVIDENCE",
                "authorized_target_commit": CLOSURE_MERGE_COMMIT,
                "release": evidence,
            },
            indent=2,
            ensure_ascii=False,
        ) + "\n",
        encoding="utf-8",
    )
    print(created.stdout.strip())
    print(f"PASS: GitHub pre-release created and evidence written to {EVIDENCE_PATH.relative_to(ROOT)}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
