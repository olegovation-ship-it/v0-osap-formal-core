# V0 OSAP v1.3.0 Post-Zenodo Historical Lifecycle Replay Compatibility Patch v0.1

This patch makes the frozen RC1 and final-GitHub-release validation layers replayable after Zenodo publication.

## Frozen predecessor snapshot

`7b38ddd6cb9bcfdc7c5713ba73a2c45d6513fbb8`

## Published successor state

- stable tag `v1.3.0` at `13bf095688bcabd5b090f188e9bd28a16237edeb`;
- GitHub final release published;
- Zenodo DOI `10.5281/zenodo.21346728` finalized;
- T140, T150, and T156 remain conditional;
- embedded checker remains `0.7.0.dev1`.

## Compatibility rule

Pre-Zenodo manifests and evidence are replayed from the frozen predecessor snapshot. Current README, status, and citation metadata may record the DOI-finalized successor lifecycle, but they may not rewrite the historical predecessor artifacts.

## Non-actions

No tag movement, GitHub Release recreation, Zenodo mutation, DOI mutation, theorem strengthening, or checker-version promotion is authorized.
