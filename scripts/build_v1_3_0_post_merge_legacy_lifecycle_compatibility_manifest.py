from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "release/v1.3.0/V1_3_0_POST_MERGE_LEGACY_LIFECYCLE_GATE_COMPATIBILITY_AND_FROZEN_MANIFEST_REPLAY_MANIFEST.json"
FILES = [
    ".github/workflows/v1-3-0-post-merge-legacy-lifecycle-compatibility.yml",
    "release/v1.3.0/V1_3_0_POST_MERGE_LEGACY_LIFECYCLE_GATE_COMPATIBILITY_AND_FROZEN_MANIFEST_REPLAY_ACCEPTANCE_GATES.md",
    "release/v1.3.0/V1_3_0_POST_MERGE_LEGACY_LIFECYCLE_GATE_COMPATIBILITY_AND_FROZEN_MANIFEST_REPLAY_RECORD.json",
    "release/v1.3.0/V1_3_0_POST_MERGE_LEGACY_LIFECYCLE_GATE_COMPATIBILITY_AND_FROZEN_MANIFEST_REPLAY_REPORT.md",
    "scripts/build_v1_3_0_post_merge_legacy_lifecycle_compatibility_manifest.py",
    "scripts/verify_rc1_gate_audit.py",
    "scripts/verify_v1_3_0_post_merge_legacy_lifecycle_compatibility.py",
    "tests/test_rc1_gate_audit.py",
    "tests/test_v1_3_0_post_merge_legacy_lifecycle_compatibility.py",
]


def main() -> int:
    payload = {
        "artifact_id": "V0_OSAP_V1_3_0_POST_MERGE_LEGACY_LIFECYCLE_GATE_COMPATIBILITY_AND_FROZEN_MANIFEST_REPLAY_MANIFEST",
        "version": "0.1",
        "date": "2026-07-15",
        "state": "POST_MERGE_LEGACY_LIFECYCLE_COMPATIBILITY_RECORDED_FROZEN_MANIFEST_REPLAY_PRESERVED",
        "baseline_merge_commit": "53dcd231aa7d5208a2360d737f01bc2e95e9450b",
        "stable_tag_target": "13bf095688bcabd5b090f188e9bd28a16237edeb",
        "zenodo_version_doi": "10.5281/zenodo.21346728",
        "files": {
            rel: hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()
            for rel in sorted(FILES)
        },
    }
    OUT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(f"PASS: legacy-lifecycle compatibility manifest generated with {len(FILES)} hashed files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
