from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, cwd=ROOT, capture_output=True, text=True, check=False)


def test_wp6_post_merge_committed_allowlist():
    assert run(
        sys.executable,
        "release/v1.4.0/tools/patch_wp6_post_merge_allowlist.py",
        "--mode",
        "committed",
    ).returncode == 0


def test_wp6_post_merge_ci_context_repair():
    assert run(
        sys.executable,
        "release/v1.4.0/tools/verify_wp6_post_merge_ci_context_repair.py",
        "--ci",
    ).returncode == 0
