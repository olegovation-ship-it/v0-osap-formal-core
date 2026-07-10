from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATTERNS = {
    "Lean": (ROOT / "lean", re.compile(r"\b(sorry|admit)\b")),
    "Coq": (ROOT / "coq", re.compile(r"\b(Admitted|admit)\b")),
}

failures: list[str] = []
for label, (directory, pattern) in PATTERNS.items():
    for path in sorted(directory.rglob("*")):
        if path.suffix not in {".lean", ".v"}:
            continue
        for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            if pattern.search(line):
                failures.append(f"{label}: {path.relative_to(ROOT)}:{line_no}: {line.strip()}")

if failures:
    print("Proof holes detected:")
    print("\n".join(failures))
    raise SystemExit(1)
print("PASS: no prohibited proof-hole markers detected.")
