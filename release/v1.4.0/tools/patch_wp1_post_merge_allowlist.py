#!/usr/bin/env python3
"""Bounded WP1 post-merge allowlist and multi-ledger succession patch v0.1.1."""
from __future__ import annotations

import argparse
import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
WP0_VERIFIER = ROOT / "scripts/verify_gate3_cluster_b_wp0.py"
WP0_TEST = ROOT / "tests/test_gate3_cluster_b_wp0.py"
WP0_PM_VERIFIER = ROOT / "scripts/verify_gate3_cluster_b_wp0_post_merge_closeout.py"
WP0_PM_TEST = ROOT / "tests/test_gate3_cluster_b_wp0_post_merge_closeout.py"
WP1_BUILDER = ROOT / "scripts/build_gate3_cluster_b_wp1.py"
WP1_VERIFIER = ROOT / "scripts/verify_gate3_cluster_b_wp1.py"
WP1_TEST = ROOT / "tests/test_gate3_cluster_b_wp1.py"

NEW_ALLOWED = (
    ".github/workflows/gate3-cluster-b-wp1-post-merge-closeout.yml",
    "scripts/build_gate3_cluster_b_wp1_post_merge_closeout.py",
    "scripts/capture_gate3_cluster_b_wp1_post_merge_evidence.py",
    "scripts/synchronize_v1_4_0_development_wp1.sh",
    "scripts/verify_gate3_cluster_b_wp1_post_merge_closeout.py",
    "tests/test_gate3_cluster_b_wp1_post_merge_closeout.py",
)
SUPERSEDED = (
    "scripts/build_gate3_cluster_b_wp1.py",
    "scripts/verify_gate3_cluster_b_wp0.py",
    "scripts/verify_gate3_cluster_b_wp0_post_merge_closeout.py",
    "scripts/verify_gate3_cluster_b_wp1.py",
    "tests/test_gate3_cluster_b_wp0.py",
    "tests/test_gate3_cluster_b_wp0_post_merge_closeout.py",
    "tests/test_gate3_cluster_b_wp1.py",
)
WP0_SUPERSEDED = set(SUPERSEDED) - {
    "scripts/build_gate3_cluster_b_wp1.py",
    "scripts/verify_gate3_cluster_b_wp1.py",
    "tests/test_gate3_cluster_b_wp1.py",
}
WP0_TEST_MARKER = "test_wp0_allowlist_covers_wp1_post_merge_closeout_controls"
WP0_PM_TEST_MARKER = "WP1_POST_MERGE_FINAL_SUCCESSOR_LEDGER_V0_1_1"
WP1_TEST_MARKER = "test_wp1_post_merge_sha256_supersession_is_exact"


def add_allowed_paths(text: str, marker: str) -> str:
    missing = [path for path in NEW_ALLOWED if f'    "{path}",' not in text]
    if missing:
        start = text.index("ALLOWED_FILES = {")
        boundary = text.index("\nALLOWED_DIRECTORIES", start)
        end = text.rfind("}", start, boundary)
        if end < start:
            raise ValueError("ALLOWED_FILES closing brace not found")
        addition = "\n    # " + marker + "\n" + "".join(
            f'    "{path}",\n' for path in missing
        )
        text = text[:end] + addition + text[end:]
    for path in NEW_ALLOWED:
        if f'    "{path}",' not in text:
            raise ValueError(f"allowlist path missing after patch: {path}")
    ast.parse(text)
    return text


def patch_wp0_verifier_text(text: str) -> str:
    return add_allowed_paths(text, "WP1_POST_MERGE_CLOSEOUT_V0_1_1_WP0")


def patch_wp0_test_text(text: str) -> str:
    if WP0_TEST_MARKER in text:
        ast.parse(text)
        return text
    block = """


def test_wp0_allowlist_covers_wp1_post_merge_closeout_controls():
    spec = importlib.util.spec_from_file_location(
        "wp0_wp1_post_merge_allowlist",
        ROOT / "scripts/verify_gate3_cluster_b_wp0.py",
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    expected = [
        ".github/workflows/gate3-cluster-b-wp1-post-merge-closeout.yml",
        "scripts/build_gate3_cluster_b_wp1_post_merge_closeout.py",
        "scripts/capture_gate3_cluster_b_wp1_post_merge_evidence.py",
        "scripts/synchronize_v1_4_0_development_wp1.sh",
        "scripts/verify_gate3_cluster_b_wp1_post_merge_closeout.py",
        "tests/test_gate3_cluster_b_wp1_post_merge_closeout.py",
    ]
    assert all(module.is_allowed_path(path) for path in expected)
"""
    text = text.rstrip("\n") + block + "\n"
    ast.parse(text)
    return text


def patch_wp0_pm_verifier_text(text: str) -> str:
    if "WP1_POST_MERGE_FINAL_LEDGER" not in text:
        anchor = """WP1_SUPERSEDED_WP0_PATHS = {
    "scripts/verify_gate3_cluster_b_wp0.py",
    "scripts/verify_gate3_cluster_b_wp0_post_merge_closeout.py",
    "tests/test_gate3_cluster_b_wp0.py",
    "tests/test_gate3_cluster_b_wp0_post_merge_closeout.py",
}
"""
        if anchor not in text:
            raise ValueError("WP0 post-merge successor constant anchor not found")
        extension = anchor + """
# WP1_POST_MERGE_FINAL_LEDGER
WP1_POST_MERGE_LEDGER = R / "GATE3_CLUSTER_B_WP1_POST_MERGE_SHA256SUMS.txt"
WP1_POST_MERGE_SUPERSEDED_WP0_PATHS = {
    "scripts/verify_gate3_cluster_b_wp0.py",
    "scripts/verify_gate3_cluster_b_wp0_post_merge_closeout.py",
    "tests/test_gate3_cluster_b_wp0.py",
    "tests/test_gate3_cluster_b_wp0_post_merge_closeout.py",
}
"""
        text = text.replace(anchor, extension, 1)
    start = text.index("def verify_ledger() -> list[str]:")
    end = text.index("\ndef git_checks(allow_main: bool) -> list[str]:", start)
    replacement = """def verify_ledger() -> list[str]:
    errors: list[str] = []
    if not LEDGER.is_file():
        return ["missing post-merge SHA256 ledger"]
    if not WP1_LEDGER.is_file():
        return ["missing WP1 successor SHA256 ledger"]
    if not WP1_POST_MERGE_LEDGER.is_file():
        return ["missing WP1 post-merge final successor SHA256 ledger"]

    historical = read_sha256_ledger(LEDGER)
    wp1_successor = read_sha256_ledger(WP1_LEDGER)
    final_successor = read_sha256_ledger(WP1_POST_MERGE_LEDGER)

    first_overlap = set(historical) & set(wp1_successor)
    if first_overlap != WP1_SUPERSEDED_WP0_PATHS:
        errors.append(
            "unexpected WP0/WP1 ledger overlap: "
            f"{sorted(first_overlap)}"
        )
    final_overlap = set(historical) & set(final_successor)
    if final_overlap != WP1_POST_MERGE_SUPERSEDED_WP0_PATHS:
        errors.append(
            "unexpected WP0/WP1-post-merge ledger overlap: "
            f"{sorted(final_overlap)}"
        )

    for rel, historical_expected in historical.items():
        file_path = ROOT / rel
        if not file_path.is_file():
            errors.append(f"ledger file missing: {rel}")
            continue
        if rel in WP1_POST_MERGE_SUPERSEDED_WP0_PATHS:
            expected = final_successor.get(rel)
        elif rel in WP1_SUPERSEDED_WP0_PATHS:
            expected = wp1_successor.get(rel)
        else:
            expected = historical_expected
        if expected is None:
            errors.append(f"successor ledger missing superseded path: {rel}")
            continue
        actual = hashlib.sha256(file_path.read_bytes()).hexdigest()
        if actual != expected:
            errors.append(f"SHA256 mismatch: {rel}")
    return errors

"""
    text = text[:start] + replacement + text[end + 1:]
    ast.parse(text)
    return text


def patch_wp0_pm_test_text(text: str) -> str:
    if WP0_PM_TEST_MARKER in text:
        ast.parse(text)
        return text
    old = '        / "GATE3_CLUSTER_B_WP1_SHA256SUMS.txt"\n'
    new = '        / "GATE3_CLUSTER_B_WP1_POST_MERGE_SHA256SUMS.txt"\n'
    if old not in text:
        raise ValueError("WP0 post-merge test successor-ledger anchor not found")
    text = text.replace(old, new, 1)
    text = text.replace(
        "def test_post_merge_sha256_ledger():",
        f"# {WP0_PM_TEST_MARKER}\ndef test_post_merge_sha256_ledger():",
        1,
    )
    ast.parse(text)
    return text


def patch_wp1_builder_text(text: str) -> str:
    marker = "WP1_POST_MERGE_BUILDER_COMPATIBILITY_V0_1_2"
    if marker in text:
        ast.parse(text)
        return text
    anchor = 'VERIFY_PATH = ROOT / "scripts/verify_gate3_cluster_b_wp1.py"\n'
    if anchor not in text:
        raise ValueError("WP1 builder verify-path anchor not found")
    text = text.replace(
        anchor,
        anchor
        + '\n# WP1_POST_MERGE_BUILDER_COMPATIBILITY_V0_1_2\n'
        + 'CANONICAL_LEDGER = ROOT / "release/v1.4.0/GATE3_CLUSTER_B_WP1_SHA256SUMS.txt"\n'
        + 'SUCCESSOR_LEDGER = ROOT / "release/v1.4.0/GATE3_CLUSTER_B_WP1_POST_MERGE_SHA256SUMS.txt"\n',
        1,
    )
    helper_anchor = "\ndef expected_outputs():\n"
    helpers = r'''

def _ledger_entries_from_text(value: str) -> dict[str, str]:
    entries: dict[str, str] = {}
    for line in value.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        digest, rel = line.split("  ", 1)
        entries[rel] = digest
    return entries


def ledger_compatibility_errors(expected_ledger: str) -> list[str]:
    if not CANONICAL_LEDGER.is_file():
        return ["missing canonical WP1 SHA256 ledger"]
    historical_text = CANONICAL_LEDGER.read_text(encoding="utf-8")
    if historical_text == expected_ledger:
        return []
    if not SUCCESSOR_LEDGER.is_file():
        return ["canonical WP1 ledger differs and successor ledger is missing"]
    historical = _ledger_entries_from_text(historical_text)
    current = _ledger_entries_from_text(expected_ledger)
    successor = _ledger_entries_from_text(SUCCESSOR_LEDGER.read_text(encoding="utf-8"))
    errors: list[str] = []
    for rel, old_digest in historical.items():
        current_digest = current.get(rel)
        if current_digest is None:
            errors.append(f"canonical WP1 path disappeared from builder surface: {rel}")
            continue
        if current_digest != old_digest and successor.get(rel) != current_digest:
            errors.append(f"successor ledger does not attest changed WP1 path: {rel}")
    for rel, current_digest in current.items():
        if rel not in historical and successor.get(rel) != current_digest:
            errors.append(f"successor ledger does not attest new WP1 namespace path: {rel}")
    return errors
'''
    if helper_anchor not in text:
        raise ValueError("WP1 builder expected-outputs anchor not found")
    text = text.replace(helper_anchor, helpers + helper_anchor, 1)
    text = text.replace(
        '    ledger_path = ROOT / "release/v1.4.0/GATE3_CLUSTER_B_WP1_SHA256SUMS.txt"\n',
        '    ledger_path = CANONICAL_LEDGER\n',
        1,
    )
    text = text.replace(
        '    if not ledger_path.is_file() or ledger_path.read_text(encoding="utf-8") != ledger: stale.append(ledger_path.relative_to(ROOT).as_posix())\n',
        '    compatibility_errors = ledger_compatibility_errors(ledger)\n    if compatibility_errors:\n        stale.append(ledger_path.relative_to(ROOT).as_posix())\n',
        1,
    )
    text = text.replace(
        '    ledger_path.write_text(ledger, encoding="utf-8")\n',
        '    if not SUCCESSOR_LEDGER.is_file():\n        ledger_path.write_text(ledger, encoding="utf-8")\n',
        1,
    )
    ast.parse(text)
    return text


def patch_wp1_verifier_text(text: str) -> str:
    text = add_allowed_paths(text, "WP1_POST_MERGE_CLOSEOUT_V0_1_1_WP1")
    anchor = 'CLOSED_WP0_RECORD_PREFIX = "release/v1.4.0/GATE3_CLUSTER_B_WP0_"\n'
    if "WP1_POST_MERGE_LEDGER" not in text:
        if anchor not in text:
            raise ValueError("WP1 verifier constant anchor not found")
        extension = anchor + """
# WP1_POST_MERGE_CLOSEOUT_EXTENSION_V0_1_1
WP1_POST_MERGE_LEDGER = "release/v1.4.0/GATE3_CLUSTER_B_WP1_POST_MERGE_SHA256SUMS.txt"
WP1_POST_MERGE_SUPERSEDED_PATHS = {
    "scripts/build_gate3_cluster_b_wp1.py",
    "scripts/verify_gate3_cluster_b_wp0.py",
    "scripts/verify_gate3_cluster_b_wp0_post_merge_closeout.py",
    "scripts/verify_gate3_cluster_b_wp1.py",
    "tests/test_gate3_cluster_b_wp0.py",
    "tests/test_gate3_cluster_b_wp0_post_merge_closeout.py",
    "tests/test_gate3_cluster_b_wp1.py",
}
"""
        text = text.replace(anchor, extension, 1)
    else:
        old = """WP1_POST_MERGE_SUPERSEDED_PATHS = {
    "scripts/build_gate3_cluster_b_wp1.py",
    "scripts/verify_gate3_cluster_b_wp1.py",
    "tests/test_gate3_cluster_b_wp1.py",
}
"""
        new = """WP1_POST_MERGE_SUPERSEDED_PATHS = {
    "scripts/build_gate3_cluster_b_wp1.py",
    "scripts/verify_gate3_cluster_b_wp0.py",
    "scripts/verify_gate3_cluster_b_wp0_post_merge_closeout.py",
    "scripts/verify_gate3_cluster_b_wp1.py",
    "tests/test_gate3_cluster_b_wp0.py",
    "tests/test_gate3_cluster_b_wp0_post_merge_closeout.py",
    "tests/test_gate3_cluster_b_wp1.py",
}
"""
        if old in text:
            text = text.replace(old, new, 1)
    helper_anchor = "def _read_sha256_ledger("
    ledger_anchor = "def ledger_errors("
    start = text.find(helper_anchor)
    if start < 0:
        start = text.index(ledger_anchor)
    end = text.index("\ndef canonical_path(value: str) -> str:", start)
    replacement = """def _read_sha256_ledger(path: Path) -> dict[str, str]:
    entries: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        expected, rel = line.split("  ", 1)
        entries[rel] = expected
    return entries


def ledger_errors(repo: Path) -> list[str]:
    historical_path = repo / "release/v1.4.0/GATE3_CLUSTER_B_WP1_SHA256SUMS.txt"
    successor_path = repo / WP1_POST_MERGE_LEDGER
    if not historical_path.is_file():
        return ["missing WP1 SHA256 ledger"]
    if not successor_path.is_file():
        return ["missing WP1 post-merge successor ledger"]
    historical = _read_sha256_ledger(historical_path)
    successor = _read_sha256_ledger(successor_path)
    overlap = set(historical) & set(successor)
    errors: list[str] = []
    if overlap != WP1_POST_MERGE_SUPERSEDED_PATHS:
        errors.append(
            "unexpected WP1/post-merge ledger overlap: "
            f"{sorted(overlap)}"
        )
    for rel, historical_expected in historical.items():
        path = repo / rel
        if not path.is_file():
            errors.append(f"ledger missing file {rel}")
            continue
        expected = (
            successor.get(rel)
            if rel in WP1_POST_MERGE_SUPERSEDED_PATHS
            else historical_expected
        )
        if expected is None:
            errors.append(f"successor ledger missing superseded path: {rel}")
            continue
        observed = hashlib.sha256(path.read_bytes()).hexdigest()
        if observed != expected:
            errors.append(f"SHA256 mismatch: {rel}")
    return errors

"""
    text = text[:start] + replacement + text[end + 1:]
    ast.parse(text)
    return text


def patch_wp1_test_text(text: str) -> str:
    old_builder_assert = '    assert (ROOT / "release/v1.4.0/GATE3_CLUSTER_B_WP1_SHA256SUMS.txt").read_text(encoding="utf-8") == ledger\n'
    new_builder_assert = '    assert module.ledger_compatibility_errors(ledger) == []\n'
    if old_builder_assert in text:
        text = text.replace(old_builder_assert, new_builder_assert, 1)
    if WP1_TEST_MARKER in text:
        old = """    superseded = {
        "scripts/build_gate3_cluster_b_wp1.py",
        "scripts/verify_gate3_cluster_b_wp1.py",
        "tests/test_gate3_cluster_b_wp1.py",
    }
"""
        new = """    superseded = {
        "scripts/build_gate3_cluster_b_wp1.py",
        "scripts/verify_gate3_cluster_b_wp0.py",
        "scripts/verify_gate3_cluster_b_wp0_post_merge_closeout.py",
        "scripts/verify_gate3_cluster_b_wp1.py",
        "tests/test_gate3_cluster_b_wp0.py",
        "tests/test_gate3_cluster_b_wp0_post_merge_closeout.py",
        "tests/test_gate3_cluster_b_wp1.py",
    }
"""
        text = text.replace(old, new, 1)
        old_ledger = (
            '        "GATE3_CLUSTER_B_WP1_SHA256SUMS.txt"\n'
        )
        # The older WP0-succession test must now resolve through the final ledger.
        before_marker = text.split(f"def {WP1_TEST_MARKER}", 1)[0]
        if old_ledger in before_marker:
            before_marker = before_marker.replace(
                old_ledger,
                '        "GATE3_CLUSTER_B_WP1_POST_MERGE_SHA256SUMS.txt"\n',
                1,
            )
            text = before_marker + f"def {WP1_TEST_MARKER}" + text.split(f"def {WP1_TEST_MARKER}", 1)[1]
        ast.parse(text)
        return text
    block = """


def test_wp1_post_merge_sha256_supersession_is_exact():
    def read_ledger(rel: str) -> dict[str, str]:
        entries: dict[str, str] = {}
        for line in (ROOT / rel).read_text(encoding="utf-8").splitlines():
            if not line.strip() or line.lstrip().startswith("#"):
                continue
            expected, path = line.split("  ", 1)
            entries[path] = expected
        return entries
    historical = read_ledger(
        "release/v1.4.0/GATE3_CLUSTER_B_WP1_SHA256SUMS.txt"
    )
    successor = read_ledger(
        "release/v1.4.0/GATE3_CLUSTER_B_WP1_POST_MERGE_SHA256SUMS.txt"
    )
    superseded = {
        "scripts/build_gate3_cluster_b_wp1.py",
        "scripts/verify_gate3_cluster_b_wp0.py",
        "scripts/verify_gate3_cluster_b_wp0_post_merge_closeout.py",
        "scripts/verify_gate3_cluster_b_wp1.py",
        "tests/test_gate3_cluster_b_wp0.py",
        "tests/test_gate3_cluster_b_wp0_post_merge_closeout.py",
        "tests/test_gate3_cluster_b_wp1.py",
    }
    assert set(historical) & set(successor) == superseded
    for rel in superseded:
        observed = hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()
        assert observed == successor[rel]
        assert successor[rel] != historical[rel]
"""
    text = text.rstrip("\n") + block + "\n"
    # Upgrade the older WP0-succession test to the final successor ledger.
    text = text.replace(
        '        "GATE3_CLUSTER_B_WP1_SHA256SUMS.txt"\n',
        '        "GATE3_CLUSTER_B_WP1_POST_MERGE_SHA256SUMS.txt"\n',
        1,
    )
    ast.parse(text)
    return text


SURFACES = (
    (WP0_VERIFIER, patch_wp0_verifier_text),
    (WP0_TEST, patch_wp0_test_text),
    (WP0_PM_VERIFIER, patch_wp0_pm_verifier_text),
    (WP0_PM_TEST, patch_wp0_pm_test_text),
    (WP1_BUILDER, patch_wp1_builder_text),
    (WP1_VERIFIER, patch_wp1_verifier_text),
    (WP1_TEST, patch_wp1_test_text),
)


def apply(check: bool) -> int:
    stale: list[str] = []
    outputs: list[tuple[Path, str]] = []
    for path, transform in SURFACES:
        source = path.read_text(encoding="utf-8")
        target = transform(source)
        outputs.append((path, target))
        if source != target:
            stale.append(path.relative_to(ROOT).as_posix())
    if check:
        print({"status": "PASS" if not stale else "FAIL", "stale": stale})
        return 0 if not stale else 1
    for path, target in outputs:
        path.write_text(target, encoding="utf-8")
    print({"status": "PASS", "updated": stale})
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    return apply(parser.parse_args().check)


if __name__ == "__main__":
    raise SystemExit(main())
