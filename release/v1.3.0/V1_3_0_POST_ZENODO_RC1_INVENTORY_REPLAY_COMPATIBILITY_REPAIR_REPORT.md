# V0 OSAP v1.3.0 Post-Zenodo RC1 Inventory Replay Compatibility Repair v0.1

## Purpose

Repair the two remaining legacy CI failures after DOI finalization:

- `RC1 gate audit / rc1-gate-audit`;
- `RC1 release closure replay / clean-room-python-replay`.

## Root cause

The historical RC1 builder still regenerated `RC1_RELEASE_MANIFEST.json` from the current working tree. Post-release compatibility changes therefore altered hashes of current verifier/workflow files, while the committed RC1 manifest correctly remained frozen.

## Repair

- `scripts/build_rc1_release_inventory.py` becomes a byte-for-byte historical replay of:
  - `RC1_THEOREM_INVENTORY.json`;
  - `RC1_RELEASE_MANIFEST.json`.
- Frozen source snapshot: `7b38ddd6cb9bcfdc7c5713ba73a2c45d6513fbb8`.
- `.github/workflows/rc1-gate-audit.yml` now checks out full history (`fetch-depth: 0`).
- A regression test verifies both invariants.

## Preservation boundary

No theorem record, stable tag, RC1 tag, GitHub Release, Zenodo record, archive, DOI, embedded checker version, or conditional theorem status is changed.
