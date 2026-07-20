#!/usr/bin/env python3
"""Idempotently extend the WP0 firewall for the bounded Gate 3 Cluster B WP1 patch."""
from __future__ import annotations

import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
VERIFIER = ROOT / "scripts/verify_gate3_cluster_b_wp0.py"
TEST_FILE = ROOT / "tests/test_gate3_cluster_b_wp0.py"

NEW_ALLOWED = [
    ".github/workflows/gate3-cluster-b-wp1.yml",
    "scripts/build_gate3_cluster_b_wp1.py",
    "scripts/verify_gate3_cluster_b_wp1.py",
    "tests/test_gate3_cluster_b_wp1.py",
]
TEST_MARKER = "def test_wp0_allowlist_covers_wp1_registry_controls():"


def patch_verifier_text(text: str) -> str:
    missing = [path for path in NEW_ALLOWED if f'    "{path}",' not in text]
    if not missing:
        return text

    anchor = "\n}\n\nALLOWED_DIRECTORIES"
    if anchor not in text:
        raise ValueError("WP0 ALLOWED_FILES insertion point not found")

    addition = "".join(f'    "{path}",\n' for path in missing)
    return text.replace(
        anchor,
        "\n" + addition + "}\n\nALLOWED_DIRECTORIES",
        1,
    )


def patch_test_text(text: str) -> str:
    if TEST_MARKER in text:
        return text

    addition = '''


def test_wp0_allowlist_covers_wp1_registry_controls():
    spec = importlib.util.spec_from_file_location(
        "wp0_wp1_allowlist",
        ROOT / "scripts/verify_gate3_cluster_b_wp0.py",
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)

    expected = [
        ".github/workflows/gate3-cluster-b-wp1.yml",
        "scripts/build_gate3_cluster_b_wp1.py",
        "scripts/verify_gate3_cluster_b_wp1.py",
        "tests/test_gate3_cluster_b_wp1.py",
    ]
    assert all(module.is_allowed_path(path) for path in expected)
'''
    return text.rstrip() + addition + "\n"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ns = ap.parse_args()

    original_v = VERIFIER.read_text(encoding="utf-8")
    original_t = TEST_FILE.read_text(encoding="utf-8")
    patched_v = patch_verifier_text(original_v)
    patched_t = patch_test_text(original_t)

    stale: list[str] = []
    if patched_v != original_v:
        stale.append(VERIFIER.relative_to(ROOT).as_posix())
    if patched_t != original_t:
        stale.append(TEST_FILE.relative_to(ROOT).as_posix())

    if ns.check:
        if stale:
            raise SystemExit(
                "ERROR: WP0 allowlist patch not applied: " + ", ".join(stale)
            )
        print("PASS")
        return 0

    if patched_v != original_v:
        VERIFIER.write_text(patched_v, encoding="utf-8")
    if patched_t != original_t:
        TEST_FILE.write_text(patched_t, encoding="utf-8")

    print(f"UPDATED={len(stale)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
