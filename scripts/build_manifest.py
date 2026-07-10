from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "release" / "bootstrap_manifest.json"
EXCLUDED = {OUTPUT.resolve()}

files = []
for path in sorted(ROOT.rglob("*")):
    if not path.is_file() or path.resolve() in EXCLUDED or ".git" in path.parts:
        continue
    if any(part in {"__pycache__", ".pytest_cache", ".lake"} for part in path.parts):
        continue
    data = path.read_bytes()
    files.append({
        "path": path.relative_to(ROOT).as_posix(),
        "sha256": hashlib.sha256(data).hexdigest(),
        "bytes": len(data),
    })

manifest = {
    "schema_version": "v1.1",
    "release_id": "V0_OSAP_v1_2_repository_bootstrap",
    "semantic_version": "v1.2.0",
    "canonicalization": "V0-OSAP-CJ-1",
    "checker_version": "0.1.0",
    "lean_version": "pending-github-actions",
    "coq_version": "pending-github-actions",
    "files": files,
    "status": "SPECIFICATION_BASELINE_ACCEPTED",
}
OUTPUT.parent.mkdir(parents=True, exist_ok=True)
OUTPUT.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
print(f"Wrote {OUTPUT.relative_to(ROOT)} with {len(files)} files.")
