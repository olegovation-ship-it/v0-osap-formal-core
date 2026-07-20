#!/usr/bin/env python3
"""Idempotently extend the WP0 firewall for the bounded post-merge closeout patch."""
from __future__ import annotations

import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
VERIFIER = ROOT / "scripts/verify_gate3_cluster_b_wp0.py"
TEST_FILE = ROOT / "tests/test_gate3_cluster_b_wp0.py"

NEW_ALLOWED = [
    ".github/workflows/gate3-cluster-b-wp0-post-merge-closeout.yml",
    "scripts/build_gate3_cluster_b_wp0_post_merge_closeout.py",
    "scripts/capture_gate3_cluster_b_wp0_post_merge_evidence.py",
    "scripts/synchronize_v1_4_0_development.sh",
    "scripts/verify_gate3_cluster_b_wp0_post_merge_closeout.py",
    "tests/test_gate3_cluster_b_wp0_post_merge_closeout.py",
]
TEST_MARKER = "def test_wp0_allowlist_covers_post_merge_closeout_controls():"


def patch_verifier(check: bool) -> bool:
    text = VERIFIER.read_text(encoding="utf-8")
    missing = [path for path in NEW_ALLOWED if f'    "{path}",' not in text]
    if not missing:
        return False
    if check:
        raise SystemExit(
            "ERROR: WP0 allowlist is missing post-merge controls: "
            + ", ".join(missing)
        )
    anchor = "\n}\n\nALLOWED_DIRECTORIES"
    if anchor not in text:
        raise SystemExit("ERROR: ALLOWED_FILES insertion point not found")
    addition = "".join(f'    "{path}",\n' for path in missing)
    text = text.replace(
        anchor,
        "\n" + addition + "}\n\nALLOWED_DIRECTORIES",
        1,
    )
    VERIFIER.write_text(text, encoding="utf-8")
    return True


def patch_tests(check: bool) -> bool:
    text = TEST_FILE.read_text(encoding="utf-8")
    if TEST_MARKER in text:
        return False
    if check:
        raise SystemExit(
            "ERROR: WP0 regression test lacks post-merge allowlist coverage"
        )
    block = """\n\n\ndef test_wp0_allowlist_covers_post_merge_closeout_controls():
    spec = importlib.util.spec_from_file_location(
        "wp0_post_merge_allowlist",
        ROOT / "scripts/verify_gate3_cluster_b_wp0.py",
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)

    expected = [
        ".github/workflows/gate3-cluster-b-wp0-post-merge-closeout.yml",
        "scripts/build_gate3_cluster_b_wp0_post_merge_closeout.py",
        "scripts/capture_gate3_cluster_b_wp0_post_merge_evidence.py",
        "scripts/synchronize_v1_4_0_development.sh",
        "scripts/verify_gate3_cluster_b_wp0_post_merge_closeout.py",
        "tests/test_gate3_cluster_b_wp0_post_merge_closeout.py",
    ]
    assert all(module.is_allowed_path(path) for path in expected)
"""
    TEST_FILE.write_text(text.rstrip() + block + "\n", encoding="utf-8")
    return True


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    changed = [patch_verifier(args.check), patch_tests(args.check)]
    print("PASS" if args.check else f"UPDATED={sum(changed)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
