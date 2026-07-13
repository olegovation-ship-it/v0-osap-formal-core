from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any

REPOSITORY = "olegovation-ship-it/v0-osap-formal-core"
AUDIT_MERGE_COMMIT = "29f9ec108efbb419fd030573b33ef5d30486d2ab"
CLOSURE_MERGE_COMMIT = "cf9a05b46b9b6f29cd85942f99155f89a49817a7"
IMMUTABLE_TAG = "v1.2.0"
IMMUTABLE_TAG_TARGET = "befa094ca3db4d5f28f5dcfbfdc4ed8a745972f3"
IMMUTABLE_DOI = "10.5281/zenodo.21306969"
CANDIDATE_TAG = "v1.3.0-rc1"
FINAL_TAG = "v1.3.0"
AUTHORIZED_STATE = "RC1_TAG_AUTHORIZED_TAG_NOT_CREATED_PRERELEASE_NOT_CREATED"


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


def commit_exists(commit: str) -> bool:
    return git("cat-file", "-e", f"{commit}^{{commit}}", check=False).returncode == 0


def is_ancestor(ancestor: str, descendant: str = "HEAD") -> bool:
    return git("merge-base", "--is-ancestor", ancestor, descendant, check=False).returncode == 0


def local_tag_exists(tag: str) -> bool:
    return git("tag", "--list", tag).stdout.strip() == tag


def remote_tag_target(remote: str, tag: str) -> str | None:
    # For annotated tags GitHub returns both refs/tags/T and refs/tags/T^{}.
    result = git("ls-remote", "--tags", remote, f"refs/tags/{tag}", f"refs/tags/{tag}^{{}}", check=False)
    if result.returncode != 0:
        return None
    peeled = None
    direct = None
    for line in result.stdout.splitlines():
        if not line.strip():
            continue
        sha, ref = line.split(maxsplit=1)
        if ref.endswith("^{}"):
            peeled = sha
        elif ref == f"refs/tags/{tag}":
            direct = sha
    return peeled or direct


def worktree_is_clean() -> bool:
    return git("status", "--porcelain").stdout.strip() == ""


def origin_matches_repository(remote: str = "origin") -> bool:
    result = git("remote", "get-url", remote, check=False)
    if result.returncode != 0:
        return False
    normalized = result.stdout.strip().removesuffix(".git")
    return normalized.endswith(REPOSITORY)
