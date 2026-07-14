from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

SNAPSHOT = "80911df7aacdac7ff411b49dcced161b98ac2071"
ROOT = Path(__file__).resolve().parents[1]
MANIFEST_REL = (
    "release/v1.3.0/"
    "V1_3_0_FINAL_RELEASE_AUTHORIZATION_MANIFEST.json"
)
OUT = ROOT / MANIFEST_REL

def historical_blob(rel_path: str) -> bytes:
    return subprocess.run(
        ["git", "show", f"{SNAPSHOT}:{rel_path}"],
        cwd=ROOT,
        check=True,
        capture_output=True,
    ).stdout

raw = historical_blob(MANIFEST_REL)
payload = json.loads(raw.decode("utf-8"))
for rel_path, expected in payload["files"].items():
    actual = hashlib.sha256(historical_blob(rel_path)).hexdigest()
    if actual != expected:
        raise SystemExit(
            "ERROR: historical final-authorization hash mismatch: "
            f"{rel_path}"
        )

OUT.write_bytes(raw)
print(
    "PASS: historical final-release authorization manifest replayed "
    f"from {SNAPSHOT} with {len(payload['files'])} hashed files."
)
