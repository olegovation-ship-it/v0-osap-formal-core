from __future__ import annotations

from pathlib import Path


def repository_root() -> Path:
    return Path(__file__).resolve().parents[2]


def schema_root() -> Path:
    return repository_root() / "schemas" / "v1.1"


def fixture_root() -> Path:
    return repository_root() / "fixtures"
