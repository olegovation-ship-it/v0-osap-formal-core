# V0 OSAP v1.3.0 Final Release Authorization Gates

**Exact target:** `13bf095688bcabd5b090f188e9bd28a16237edeb`  
**Stable tag:** `v1.3.0`  
**State encoded by patch:** `FINAL_RELEASE_AUTHORIZED / STABLE_TAG_NOT_CREATED / FINAL_GITHUB_RELEASE_NOT_CREATED / ZENODO_NOT_PUBLISHED`

| Gate | Requirement | Patch state |
|---|---|---|
| FR-A00 | PR #15 merged and exact evidence-closure commit exists | target pinned |
| FR-A01 | RC1 evidence-closure record and manifest are present | executable check |
| FR-A02 | `v1.3.0-rc1` peels to `cf9a05b46b9b6f29cd85942f99155f89a49817a7` | executable tag check |
| FR-A03 | post-merge RC1 evidence workflows were observed successful | recorded evidence |
| FR-A04 | `v1.2.0` remains at `befa094ca3db4d5f28f5dcfbfdc4ed8a745972f3` | executable tag check |
| FR-A05 | DOI remains `10.5281/zenodo.21306969` | executable metadata check |
| FR-A06 | `v1.3.0` is absent before authorization merge | executable pre-tag check |
| FR-A07 | `13bf095688bcabd5b090f188e9bd28a16237edeb` is the only authorized stable target | completed |
| FR-A08 | annotated-tag message is final and internally consistent | executable check |
| FR-A09 | GitHub final-release notes and metadata are consistent | executable check |
| FR-A10 | creation scripts are dry-run by default | executable tests |
| FR-A11 | explicit confirmation is required | executable tests |
| FR-A12 | authorization workflow performs validation only | executable workflow scan |
| FR-A13 | this patch passes CI and is merged | pending after application |
| FR-A14 | stable tag peels exactly to the authorized target | post-merge operation |
| FR-A15 | GitHub final release is non-draft and non-prerelease | post-tag operation |
| FR-A16 | RC1 pre-release remains historical and unmodified | enforced |
| FR-A17 | Zenodo publication and DOI mutation remain unauthorized | enforced |

## Creation rule

The stable tag may be created only after FR-A13 passes. The command must explicitly name
the full authorized target. Lightweight tags, implicit targets, tag movement, and tag
replacement are prohibited.

The final GitHub Release may be created only after the remote annotated tag exists and
peels exactly to the authorized target. The command must use `--verify-tag`, must not use
`--prerelease`, and must use the prepared notes.
