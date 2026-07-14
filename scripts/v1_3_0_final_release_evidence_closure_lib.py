from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any

REPOSITORY = "olegovation-ship-it/v0-osap-formal-core"
FINAL_TAG = "v1.3.0"
FINAL_TARGET = "13bf095688bcabd5b090f188e9bd28a16237edeb"
FINAL_AUTHORIZATION_MERGE_COMMIT = "80911df7aacdac7ff411b49dcced161b98ac2071"
RC1_TAG = "v1.3.0-rc1"
RC1_TARGET = "cf9a05b46b9b6f29cd85942f99155f89a49817a7"
IMMUTABLE_TAG = "v1.2.0"
IMMUTABLE_TARGET = "befa094ca3db4d5f28f5dcfbfdc4ed8a745972f3"
IMMUTABLE_DOI = "10.5281/zenodo.21306969"

EXPECTED_RELEASE_NAME = "V0 OSAP v1.3.0 — Stable Release"
EXPECTED_RELEASE_URL = (
    "https://github.com/olegovation-ship-it/"
    "v0-osap-formal-core/releases/tag/v1.3.0"
)
EXPECTED_PUBLISHED_AT = "2026-07-13T21:40:22Z"
MACHINE_STATE = (
    "FINAL_RELEASE_EVIDENCE_CLOSED_STABLE_TAG_CREATED_"
    "FINAL_GITHUB_RELEASE_CREATED_ZENODO_NOT_PUBLISHED"
)
HUMAN_STATE = (
    "FINAL_RELEASE_EVIDENCE_CLOSED / STABLE_TAG_CREATED / "
    "FINAL_GITHUB_RELEASE_CREATED / ZENODO_NOT_PUBLISHED"
)

RELEASE_DIR = Path("release/v1.3.0")
EVIDENCE_PATH = RELEASE_DIR / "V1_3_0_GITHUB_FINAL_RELEASE_EVIDENCE.json"
RECORD_PATH = RELEASE_DIR / "V1_3_0_FINAL_RELEASE_EVIDENCE_CLOSURE_RECORD.json"
MANIFEST_PATH = RELEASE_DIR / "V1_3_0_FINAL_RELEASE_EVIDENCE_CLOSURE_MANIFEST.json"

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

def git(*args: str, check: bool = True) -> str:
    return run("git", *args, check=check).stdout.strip()

def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))

def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()

def tag_exists(tag: str) -> bool:
    return git("tag", "--list", tag) == tag

def tag_target(tag: str) -> str | None:
    if not tag_exists(tag):
        return None
    return git("rev-list", "-n", "1", tag)

def tag_object_type(tag: str) -> str | None:
    result = run("git", "cat-file", "-t", f"refs/tags/{tag}", check=False)
    return result.stdout.strip() if result.returncode == 0 else None

def tag_object_sha(tag: str) -> str | None:
    if not tag_exists(tag):
        return None
    return git("rev-parse", f"refs/tags/{tag}")

def remote_tag_map(tag: str) -> dict[str, str]:
    output = git(
        "ls-remote",
        "origin",
        f"refs/tags/{tag}",
        f"refs/tags/{tag}^{{}}",
    )
    result: dict[str, str] = {}
    for line in output.splitlines():
        sha, ref = line.split(maxsplit=1)
        result[ref] = sha
    return result
