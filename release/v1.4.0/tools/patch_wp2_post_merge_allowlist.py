#!/usr/bin/env python3
"""Bounded WP2 post-merge allowlist and successor-ledger compatibility patch v0.1."""
from __future__ import annotations

import argparse
import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BUILDER = ROOT / "scripts/build_gate3_cluster_b_wp2.py"
VERIFIER = ROOT / "scripts/verify_gate3_cluster_b_wp2.py"

NEW_ALLOWED = (
    ".github/workflows/gate3-cluster-b-wp2-post-merge-closeout.yml",
    "docs/gate3/cluster_b/WP2_POST_MERGE_ARCHIVAL_CLOSEOUT_AND_DEVELOPMENT_BRANCH_SYNCHRONIZATION.md",
    "release/v1.4.0/tools/patch_wp2_post_merge_allowlist.py",
    "scripts/build_gate3_cluster_b_wp2_post_merge_closeout.py",
    "scripts/capture_gate3_cluster_b_wp2_post_merge_evidence.py",
    "scripts/synchronize_v1_4_0_development_wp2.sh",
    "scripts/verify_gate3_cluster_b_wp2_post_merge_closeout.py",
    "tests/test_gate3_cluster_b_wp2_post_merge_closeout.py",
)
MARKER = "WP2_POST_MERGE_SUCCESSOR_LEDGER_COMPATIBILITY_V0_1"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected exactly one anchor, found {count}")
    return text.replace(old, new, 1)


def patch_builder(text: str) -> str:
    if MARKER in text:
        ast.parse(text)
        return text

    anchor = 'SCHEMAS = ROOT / "schemas/v1.4.0"\n'
    extension = anchor + f'''
# {MARKER}
CANONICAL_LEDGER = RELEASE / "GATE3_CLUSTER_B_WP2_SHA256SUMS.txt"
SUCCESSOR_LEDGER = RELEASE / "GATE3_CLUSTER_B_WP2_POST_MERGE_SHA256SUMS.txt"


def is_post_merge_schema(path: Path) -> bool:
    name = path.name
    return "_post_merge_" in name or "_development_branch_synchronization_" in name


def is_post_merge_record(path: Path) -> bool:
    name = path.name
    return "_POST_MERGE_" in name or "_DEVELOPMENT_BRANCH_SYNCHRONIZATION_" in name
'''
    text = replace_once(text, anchor, extension, "builder constants")

    old = '    schemas = sorted(path.relative_to(ROOT).as_posix() for path in SCHEMAS.glob("gate3_cluster_b_wp2_*.schema.json"))\n'
    new = '''    schemas = sorted(
        path.relative_to(ROOT).as_posix()
        for path in SCHEMAS.glob("gate3_cluster_b_wp2_*.schema.json")
        if not is_post_merge_schema(path)
    )
'''
    text = replace_once(text, old, new, "builder schema bundle")

    old = '    candidates.extend(sorted(SCHEMAS.glob("gate3_cluster_b_wp2_*.schema.json")))\n'
    new = '''    candidates.extend(sorted(
        path for path in SCHEMAS.glob("gate3_cluster_b_wp2_*.schema.json")
        if not is_post_merge_schema(path)
    ))
'''
    text = replace_once(text, old, new, "builder schema ledger filter")

    old = '    candidates.extend(sorted(RELEASE.glob("GATE3_CLUSTER_B_WP2_*.json")))\n'
    new = '''    candidates.extend(sorted(
        path for path in RELEASE.glob("GATE3_CLUSTER_B_WP2_*.json")
        if not is_post_merge_record(path)
    ))
'''
    text = replace_once(text, old, new, "builder record ledger filter")

    helper_anchor = "\ndef main() -> int:\n"
    helpers = r'''

def parse_ledger_bytes(value: bytes) -> dict[str, str]:
    entries: dict[str, str] = {}
    for line in value.decode("utf-8").splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        digest, rel = line.split("  ", 1)
        entries[rel] = digest
    return entries


def canonical_ledger_compatibility_errors(expected: bytes) -> list[str]:
    if not CANONICAL_LEDGER.is_file():
        return ["missing canonical WP2 SHA256 ledger"]
    historical_bytes = CANONICAL_LEDGER.read_bytes()
    if historical_bytes == expected:
        return []
    if not SUCCESSOR_LEDGER.is_file():
        return ["canonical WP2 ledger differs and successor ledger is missing"]

    historical = parse_ledger_bytes(historical_bytes)
    current = parse_ledger_bytes(expected)
    successor = parse_ledger_bytes(SUCCESSOR_LEDGER.read_bytes())
    errors: list[str] = []

    for rel, historical_digest in historical.items():
        current_digest = current.get(rel)
        if current_digest is None:
            errors.append(f"canonical WP2 path disappeared from builder surface: {rel}")
            continue
        if current_digest != historical_digest and successor.get(rel) != current_digest:
            errors.append(f"successor ledger does not attest changed WP2 path: {rel}")

    for rel, current_digest in current.items():
        if rel not in historical and successor.get(rel) != current_digest:
            errors.append(f"successor ledger does not attest new canonical WP2 path: {rel}")
    return errors


def check_or_write_canonical_ledger(expected: bytes, check: bool) -> list[str]:
    if not check and not SUCCESSOR_LEDGER.is_file():
        CANONICAL_LEDGER.write_bytes(expected)
        return []
    return canonical_ledger_compatibility_errors(expected)
'''
    if helper_anchor not in text:
        raise RuntimeError("builder main anchor not found")
    text = text.replace(helper_anchor, helpers + helper_anchor, 1)

    old = '    write_or_check(RELEASE / "GATE3_CLUSTER_B_WP2_SHA256SUMS.txt", ledger_bytes(), args.check, errors)\n'
    new = '    errors.extend(check_or_write_canonical_ledger(ledger_bytes(), args.check))\n'
    text = replace_once(text, old, new, "builder ledger call")
    ast.parse(text)
    return text


def patch_verifier(text: str) -> str:
    if MARKER in text:
        ast.parse(text)
        return text

    start = text.index("ALLOWED_NEW_FILES = {")
    boundary = text.index("\nALLOWED_NEW_PREFIXES", start)
    end = text.rfind("}", start, boundary)
    if end < start:
        raise RuntimeError("ALLOWED_NEW_FILES closing brace not found")
    missing = [path for path in NEW_ALLOWED if f'    "{path}",' not in text[start:boundary]]
    addition = "\n    # " + MARKER + "\n" + "".join(f'    "{path}",\n' for path in missing)
    text = text[:end] + addition + text[end:]

    anchor = 'SCHEMAS = ROOT / "schemas/v1.4.0"\n'
    extension = anchor + f'''
# {MARKER}
CANONICAL_LEDGER = RELEASE / "GATE3_CLUSTER_B_WP2_SHA256SUMS.txt"
SUCCESSOR_LEDGER = RELEASE / "GATE3_CLUSTER_B_WP2_POST_MERGE_SHA256SUMS.txt"
POST_MERGE_SUPERSEDED_PATHS = {{
    "scripts/build_gate3_cluster_b_wp2.py",
    "scripts/verify_gate3_cluster_b_wp2.py",
}}
'''
    text = replace_once(text, anchor, extension, "verifier constants")

    fn_start = text.index("def ledger_errors() -> list[str]:")
    fn_end = text.index("\ndef is_allowed_new", fn_start)
    replacement = r'''def read_sha256_ledger(path: Path) -> dict[str, str]:
    entries: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        digest, rel = line.split("  ", 1)
        entries[rel] = digest
    return entries


def ledger_errors() -> list[str]:
    if not CANONICAL_LEDGER.is_file():
        return ["missing WP2 SHA256 ledger"]
    historical = read_sha256_ledger(CANONICAL_LEDGER)
    successor = read_sha256_ledger(SUCCESSOR_LEDGER) if SUCCESSOR_LEDGER.is_file() else {}
    errors: list[str] = []

    overlap = set(historical) & set(successor)
    if successor and overlap != POST_MERGE_SUPERSEDED_PATHS:
        errors.append(f"unexpected WP2/post-merge ledger overlap: {sorted(overlap)}")

    for rel, historical_expected in historical.items():
        target = ROOT / rel
        if not target.is_file():
            errors.append(f"ledger missing file: {rel}")
            continue
        expected = successor.get(rel) if rel in POST_MERGE_SUPERSEDED_PATHS else historical_expected
        if expected is None:
            errors.append(f"successor ledger missing superseded path: {rel}")
            continue
        if sha256(target) != expected:
            errors.append(f"SHA256 mismatch: {rel}")

    if successor:
        for rel, expected in successor.items():
            target = ROOT / rel
            if not target.is_file():
                errors.append(f"successor ledger missing file: {rel}")
            elif sha256(target) != expected:
                errors.append(f"successor SHA256 mismatch: {rel}")
    return errors

'''
    text = text[:fn_start] + replacement + text[fn_end + 1:]
    ast.parse(text)
    return text


def expected_texts() -> dict[Path, str]:
    return {
        BUILDER: patch_builder(BUILDER.read_text(encoding="utf-8")),
        VERIFIER: patch_verifier(VERIFIER.read_text(encoding="utf-8")),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    stale: list[str] = []
    for path, expected in expected_texts().items():
        if args.check:
            if path.read_text(encoding="utf-8") != expected:
                stale.append(path.relative_to(ROOT).as_posix())
        else:
            path.write_text(expected, encoding="utf-8")
    print({
        "status": "PASS" if not stale else "FAIL",
        "mode": "CHECK" if args.check else "WRITE",
        "stale": stale,
    })
    return 0 if not stale else 1


if __name__ == "__main__":
    raise SystemExit(main())
