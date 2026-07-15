from __future__ import annotations

import json
import subprocess
from pathlib import Path

from rc1_audit_lib import audit_inventory

ROOT = Path(__file__).resolve().parents[1]
RELEASE = ROOT / "release/v1.3.0"
HISTORICAL_SNAPSHOT = "7b38ddd6cb9bcfdc7c5713ba73a2c45d6513fbb8"

FROZEN_OUTPUTS = (
    "release/v1.3.0/RC1_THEOREM_INVENTORY.json",
    "release/v1.3.0/RC1_RELEASE_MANIFEST.json",
)


def run(*args: str, check: bool = True) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        list(args),
        cwd=ROOT,
        check=check,
        capture_output=True,
    )


def historical_blob(rel_path: str) -> bytes:
    return run("git", "show", f"{HISTORICAL_SNAPSHOT}:{rel_path}").stdout


def main() -> int:
    if run(
        "git",
        "merge-base",
        "--is-ancestor",
        HISTORICAL_SNAPSHOT,
        "HEAD",
        check=False,
    ).returncode != 0:
        raise SystemExit(
            "ERROR: frozen RC1 replay snapshot is not an ancestor of HEAD: "
            + HISTORICAL_SNAPSHOT
        )

    blobs = {rel: historical_blob(rel) for rel in FROZEN_OUTPUTS}

    inventory = json.loads(
        blobs["release/v1.3.0/RC1_THEOREM_INVENTORY.json"].decode("utf-8")
    )
    manifest = json.loads(
        blobs["release/v1.3.0/RC1_RELEASE_MANIFEST.json"].decode("utf-8")
    )

    diagnostics = audit_inventory(inventory)
    if diagnostics:
        raise SystemExit(
            "ERROR: frozen RC1 inventory failed structural audit: "
            + repr(diagnostics)
        )

    if inventory.get("record_count") != 36:
        raise SystemExit("ERROR: frozen RC1 inventory record count is not 36")
    if inventory.get("theorem_range") != "T121-T156":
        raise SystemExit("ERROR: frozen RC1 theorem range mismatch")
    if manifest.get("artifact_id") != "V0_OSAP_V1_3_0_RC1_RELEASE_MANIFEST":
        raise SystemExit("ERROR: frozen RC1 manifest artifact id mismatch")
    if manifest.get("theorem_inventory_sha256") != inventory.get(
        "inventory_sha256"
    ):
        raise SystemExit("ERROR: frozen RC1 inventory/manifest hash mismatch")

    for rel, blob in blobs.items():
        path = ROOT / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(blob)

    print(
        "PASS: historical RC1 theorem inventory and release manifest replayed "
        f"byte-for-byte from {HISTORICAL_SNAPSHOT}."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
