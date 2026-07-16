from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = (
    ROOT
    / "release/v1.3.0/"
    "V1_3_0_POST_MERGE_PUBLICATION_LIFECYCLE_REPLAY_AND_FROZEN_ZENODO_"
    "MANIFEST_COMPATIBILITY_MANIFEST.json"
)
FILES = [
    ".github/workflows/v1-3-0-post-merge-publication-lifecycle-replay-compatibility.yml",
    "release/v1.3.0/V1_3_0_POST_MERGE_PUBLICATION_LIFECYCLE_REPLAY_AND_FROZEN_ZENODO_MANIFEST_COMPATIBILITY_ACCEPTANCE_GATES.md",
    "release/v1.3.0/V1_3_0_POST_MERGE_PUBLICATION_LIFECYCLE_REPLAY_AND_FROZEN_ZENODO_MANIFEST_COMPATIBILITY_RECORD.json",
    "release/v1.3.0/V1_3_0_POST_MERGE_PUBLICATION_LIFECYCLE_REPLAY_AND_FROZEN_ZENODO_MANIFEST_COMPATIBILITY_REPORT.md",
    "scripts/build_v1_3_0_post_merge_publication_lifecycle_replay_compatibility_manifest.py",
    "scripts/build_v1_3_0_zenodo_publication_evidence_closure_manifest.py",
    "scripts/verify_v1_3_0_final_release_evidence_closure.py",
    "scripts/verify_v1_3_0_post_merge_publication_lifecycle_replay_compatibility.py",
    "scripts/verify_v1_3_0_zenodo_publication_evidence_closure.py",
    "tests/test_v1_3_0_final_release_evidence_closure.py",
    "tests/test_v1_3_0_post_merge_publication_lifecycle_replay_compatibility.py",
    "tests/test_v1_3_0_zenodo_publication_evidence_closure.py",
]


def main() -> int:
    payload = {
        "artifact_id": (
            "V0_OSAP_V1_3_0_POST_MERGE_PUBLICATION_LIFECYCLE_REPLAY_AND_"
            "FROZEN_ZENODO_MANIFEST_COMPATIBILITY_MANIFEST"
        ),
        "version": "0.1",
        "date": "2026-07-16",
        "state": (
            "POST_MERGE_PUBLICATION_LIFECYCLE_REPLAY_COMPATIBLE_"
            "FROZEN_ZENODO_MANIFEST_REPLAY_PRESERVED"
        ),
        "parent_commit": "c25983fa72aa98bd0d67352821b731ad6542a00b",
        "zenodo_snapshot": "53dcd231aa7d5208a2360d737f01bc2e95e9450b",
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
    print(
        "PASS: post-merge publication-lifecycle compatibility manifest "
        f"generated with {len(FILES)} hashed files."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
