from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_wp6_post_merge_push_context_repair():
    cp = subprocess.run(
        [
            sys.executable,
            "release/v1.4.0/tools/"
            "verify_wp6_post_merge_push_context_repair.py",
            "--mode",
            "auto",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert cp.returncode == 0, cp.stdout + cp.stderr
