from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any

REPOSITORY = "olegovation-ship-it/v0-osap-formal-core"
AUDIT_MERGE_COMMIT = "29f9ec108efbb419fd030573b33ef5d30486d2ab"
CLOSURE_MERGE_COMMIT = "cf9a05b46b9b6f29cd85942f99155f89a49817a7"
AUTHORIZATION_MERGE_COMMIT = "cc1148f4c01cec2e2fca05651d02edc18fdc7312"

IMMUTABLE_TAG = "v1.2.0"
IMMUTABLE_TAG_TARGET = "befa094ca3db4d5f28f5dcfbfdc4ed8a745972f3"
IMMUTABLE_DOI = "10.5281/zenodo.21306969"

CANDIDATE_TAG = "v1.3.0-rc1"
FINAL_TAG = "v1.3.0"
CANDIDATE_TARGET = CLOSURE_MERGE_COMMIT

MACHINE_STATE = "RC1_RELEASE_EVIDENCE_CLOSED_TAG_CREATED_PRERELEASE_CREATED_FINAL_RELEASE_NOT_CREATED"
HUMAN_STATE = (
    "RC1_RELEASE_EVIDENCE_CLOSED / TAG_CREATED / "
    "PRERELEASE_CREATED / FINAL_RELEASE_NOT_CREATED"
)

EXPECTED_RELEASE_NAME = "V0 OSAP v1.3.0-rc1 — Release Candidate 1"
EXPECTED_RELEASE_URL = (
    "https://github.com/olegovation-ship-it/"
    "v0-osap-formal-core/releases/tag/v1.3.0-rc1"
)
EXPECTED_PUBLISHED_AT = "2026-07-13T18:15:33Z"

RELEASE_DIR = Path("release/v1.3.0")
EVIDENCE_PATH = RELEASE_DIR / "RC1_GITHUB_PRERELEASE_EVIDENCE.json"
RECORD_PATH = RELEASE_DIR / "RC1_RELEASE_EVIDENCE_CLOSURE_RECORD.json"
MANIFEST_PATH = RELEASE_DIR / "RC1_RELEASE_EVIDENCE_CLOSURE_MANIFEST.json"
REPORT_PATH = (
    RELEASE_DIR
    / "RC1_RELEASE_EVIDENCE_CLOSURE_AND_HISTORICAL_PRESERVATION_REPORT.md"
)
GATES_PATH = RELEASE_DIR / "RC1_RELEASE_EVIDENCE_CLOSURE_ACCEPTANCE_GATES.md"


def repository_root() -> Path:
    return Path(__file__).resolve().parents[1]


def run(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [*args],
        cwd=repository_root(),
        text=True,
        capture_output=True,
        check=check,
    )


def git(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return run("git", *args, check=check)


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, ensure_ascii=False, sort_keys=False) + "\n",
        encoding="utf-8",
    )


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def local_tag_exists(tag: str) -> bool:
    return git("tag", "--list", tag).stdout.strip() == tag


def local_tag_target(tag: str) -> str | None:
    if not local_tag_exists(tag):
        return None
    return git("rev-list", "-n", "1", tag).stdout.strip() or None


def tag_object_type(tag: str) -> str | None:
    if not local_tag_exists(tag):
        return None
    result = git("cat-file", "-t", f"refs/tags/{tag}", check=False)
    return result.stdout.strip() if result.returncode == 0 else None


def commit_exists(commit: str) -> bool:
    return git("cat-file", "-e", f"{commit}^{{commit}}", check=False).returncode == 0


def is_ancestor(ancestor: str, descendant: str = "HEAD") -> bool:
    return git(
        "merge-base", "--is-ancestor", ancestor, descendant, check=False
    ).returncode == 0
