from __future__ import annotations

import hashlib
import json
import re
import subprocess
from pathlib import Path
from typing import Any

AUDIT_MERGE_COMMIT = "29f9ec108efbb419fd030573b33ef5d30486d2ab"
IMMUTABLE_TAG = "v1.2.0"
IMMUTABLE_TAG_TARGET = "befa094ca3db4d5f28f5dcfbfdc4ed8a745972f3"
IMMUTABLE_DOI = "10.5281/zenodo.21306969"
CANDIDATE_TAG = "v1.3.0-rc1"
FINAL_TAG = "v1.3.0"


def repository_root() -> Path:
    return Path(__file__).resolve().parents[1]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=False) + "\n",
        encoding="utf-8",
    )


def git(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=repository_root(),
        text=True,
        capture_output=True,
        check=check,
    )


def expected_theorem_ids() -> list[str]:
    return [f"T{i}" for i in range(121, 157)]


def tag_exists(tag: str) -> bool:
    result = git("tag", "--list", tag)
    return result.stdout.strip() == tag


def commit_exists(commit: str) -> bool:
    return git("cat-file", "-e", f"{commit}^{{commit}}", check=False).returncode == 0


def is_ancestor(ancestor: str, descendant: str = "HEAD") -> bool:
    return git("merge-base", "--is-ancestor", ancestor, descendant, check=False).returncode == 0


def forbidden_release_commands(text: str) -> list[str]:
    patterns = {
        "git-tag": r"(?im)^\s*(?:-\s*)?run:\s*.*\bgit\s+tag\b",
        "gh-release": r"(?im)^\s*(?:-\s*)?run:\s*.*\bgh\s+release\s+create\b",
        "github-release-api": r"(?im)^\s*(?:-\s*)?run:\s*.*api\.github\.com/.*/releases",
        "zenodo-deposition": r"(?im)^\s*(?:-\s*)?run:\s*.*zenodo.*deposit",
    }
    return [name for name, pattern in patterns.items() if re.search(pattern, text)]
