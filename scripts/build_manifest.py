from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "release" / "bootstrap_manifest.json"
VERSIONS = ROOT / "release" / "compiler_versions.json"
EXCLUDED = {OUTPUT.resolve()}
EXCLUDED_PARTS = {
    ".git",
    "__pycache__",
    ".pytest_cache",
    ".lake",
    ".mypy_cache",
    ".ruff_cache",
    ".tox",
    ".nox",
}
EXCLUDED_SUFFIXES = {
    ".pyc", ".pyo", ".vo", ".vok", ".vos", ".glob", ".aux",
}
EXCLUDED_NAMES = {
    "Makefile.coq", "Makefile.coq.conf", ".coverage",
}

metadata = json.loads(VERSIONS.read_text(encoding="utf-8"))

files = []
for path in sorted(ROOT.rglob("*")):
    if not path.is_file() or path.resolve() in EXCLUDED:
        continue
    if any(part in EXCLUDED_PARTS or part.endswith(".egg-info") for part in path.parts):
        continue
    if path.suffix in EXCLUDED_SUFFIXES or path.name in EXCLUDED_NAMES:
        continue
    data = path.read_bytes()
    files.append({
        "path": path.relative_to(ROOT).as_posix(),
        "sha256": hashlib.sha256(data).hexdigest(),
        "bytes": len(data),
    })

manifest = {
    "schema_version": "v1.1",
    "release_id": "V0_OSAP_v1_2_0_compiler_passed_closure",
    "semantic_version": "v1.2.0",
    "canonicalization": "V0-OSAP-CJ-1",
    "git_commit": metadata["validated_commit"],
    "checker_version": metadata["checker_version"],
    "lean_version": metadata["lean_version"],
    "coq_version": metadata["coq_version"],
    "files": files,
    "status": "DUAL_BACKEND_ACCEPTED",
}
OUTPUT.parent.mkdir(parents=True, exist_ok=True)
OUTPUT.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
print(f"Wrote {OUTPUT.relative_to(ROOT)} with {len(files)} files.")
