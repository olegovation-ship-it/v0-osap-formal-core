from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any

REPOSITORY = "olegovation-ship-it/v0-osap-formal-core"
FINAL_TAG = "v1.3.0"
FINAL_TARGET = "13bf095688bcabd5b090f188e9bd28a16237edeb"
FINAL_RELEASE_EVIDENCE_MERGE_COMMIT = "7b38ddd6cb9bcfdc7c5713ba73a2c45d6513fbb8"
RC1_TAG = "v1.3.0-rc1"
RC1_TARGET = "cf9a05b46b9b6f29cd85942f99155f89a49817a7"
IMMUTABLE_TAG = "v1.2.0"
IMMUTABLE_TARGET = "befa094ca3db4d5f28f5dcfbfdc4ed8a745972f3"
IMMUTABLE_DOI = "10.5281/zenodo.21306969"

ZENODO_RECORD_ID = 21346728
ZENODO_DOI = "10.5281/zenodo.21346728"
ZENODO_URL = "https://zenodo.org/records/21346728"
ZENODO_TITLE = "V0 OSAP Formal Core v1.3.0 — T121–T156 Stable Release"
ZENODO_PUBLICATION_DATE = "2026-07-13"
ZENODO_ARCHIVE = "olegovation-ship-it/v0-osap-formal-core-v1.3.0.zip"

MACHINE_STATE = (
    "ZENODO_PUBLICATION_EVIDENCE_CLOSED_DOI_FINALIZED_"
    "STABLE_TAG_CREATED_FINAL_GITHUB_RELEASE_CREATED_ZENODO_PUBLISHED"
)
HUMAN_STATE = (
    "ZENODO_PUBLICATION_EVIDENCE_CLOSED / DOI_FINALIZED / "
    "STABLE_TAG_CREATED / FINAL_GITHUB_RELEASE_CREATED / ZENODO_PUBLISHED"
)

RELEASE_DIR = Path("release/v1.3.0")
EVIDENCE_PATH = RELEASE_DIR / "V1_3_0_ZENODO_PUBLICATION_EVIDENCE.json"
RECORD_PATH = RELEASE_DIR / "V1_3_0_ZENODO_PUBLICATION_EVIDENCE_CLOSURE_RECORD.json"
MANIFEST_PATH = RELEASE_DIR / "V1_3_0_ZENODO_PUBLICATION_EVIDENCE_CLOSURE_MANIFEST.json"

FROZEN_PREDECESSORS = [
    "release/v1.3.0/V1_3_0_FINAL_RELEASE_EVIDENCE_CLOSURE_MANIFEST.json",
    "release/v1.3.0/V1_3_0_FINAL_RELEASE_EVIDENCE_CLOSURE_RECORD.json",
    "release/v1.3.0/V1_3_0_FINAL_RELEASE_AUTHORIZATION_MANIFEST.json",
    "release/v1.3.0/V1_3_0_FINAL_RELEASE_AUTHORIZATION_RECORD.json",
    "release/v1.3.0/RC1_RELEASE_EVIDENCE_CLOSURE_MANIFEST.json",
    "release/v1.3.0/RC1_RELEASE_EVIDENCE_CLOSURE_RECORD.json",
]

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
