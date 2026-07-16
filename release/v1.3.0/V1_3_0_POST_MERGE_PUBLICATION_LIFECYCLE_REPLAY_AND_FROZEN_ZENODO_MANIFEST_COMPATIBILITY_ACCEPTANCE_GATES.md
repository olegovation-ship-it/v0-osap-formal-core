# V0 OSAP v1.3.0 Post-Merge Publication Lifecycle Replay Acceptance Gates

- [x] Final-release evidence is replayed from commit `7b38ddd6cb9bcfdc7c5713ba73a2c45d6513fbb8`.
- [x] The post-merge successor marker is accepted only with all three companion markers.
- [x] Post-merge acceptance requires stable target `13bf095688bcabd5b090f188e9bd28a16237edeb`.
- [x] Post-merge acceptance requires DOI `10.5281/zenodo.21346728`.
- [x] Historical DOI `10.5281/zenodo.21306969` remains visible and immutable.
- [x] Checker component remains `0.7.0.dev1`.
- [x] T140, T150, and T156 remain conditional.
- [x] The Zenodo publication-evidence manifest is replayed byte-for-byte from commit `53dcd231aa7d5208a2360d737f01bc2e95e9450b`.
- [x] Historical manifest entries are checked against snapshot blobs, not current post-merge status surfaces.
- [x] Current README, changelog, and status surfaces are validated as guarded successor surfaces.
- [x] No release, tag, Zenodo, DOI, archive, theorem, or checker mutation is authorized.
- [x] No historical SHA-256 value is replaced.

Acceptance state:

`POST_MERGE_PUBLICATION_LIFECYCLE_REPLAY_COMPATIBLE / FROZEN_ZENODO_MANIFEST_REPLAY_PRESERVED`
