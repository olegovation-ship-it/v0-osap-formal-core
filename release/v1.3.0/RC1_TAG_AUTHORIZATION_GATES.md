# V0 OSAP v1.3.0 RC1 Tag-Authorization Gates

**Closure merge:** `cf9a05b46b9b6f29cd85942f99155f89a49817a7`
**Candidate tag:** `v1.3.0-rc1`
**State after patch application:** `RC1_TAG_AUTHORIZED / TAG_NOT_CREATED / PRERELEASE_NOT_CREATED`

| Gate | Requirement | State encoded by patch |
|---|---|---|
| RC1-T00 | PR #13 merged and exact closure commit exists | `cf9a05b46b9b6f29cd85942f99155f89a49817a7` pinned |
| RC1-T01 | Closure commit is an ancestor of current development HEAD | executable check |
| RC1-T02 | `main` and `v1.3.0-development` were synchronized to the closure commit | recorded evidence |
| RC1-T03 | Post-merge Python, schema, audit, readiness, replay, Lean, and Coq checks passed | recorded evidence |
| RC1-T04 | Historical `v1.2.0` still targets `befa094ca3db4d5f28f5dcfbfdc4ed8a745972f3` | executable check |
| RC1-T05 | DOI remains `10.5281/zenodo.21306969` | executable metadata check |
| RC1-T06 | `v1.3.0-rc1` and `v1.3.0` do not yet exist | executable pre-tag check |
| RC1-T07 | Exact target `cf9a05b46b9b6f29cd85942f99155f89a49817a7` is separately authorized | completed |
| RC1-T08 | Annotated tag message is final and internally consistent | executable check |
| RC1-T09 | GitHub pre-release title, notes, and metadata are consistent | executable check |
| RC1-T10 | Creation scripts are dry-run by default and require explicit confirmation | executable tests |
| RC1-T11 | CI workflow contains no tag or release command | executable check |
| RC1-T12 | Authorization patch passes CI and is merged | pending after application |
| RC1-T13 | Annotated tag resolves exactly to the authorized target | post-merge execution |
| RC1-T14 | GitHub Release is a non-draft pre-release for the authorized tag | post-tag execution |
| RC1-T15 | Final tag, Zenodo version, and DOI mutation remain unauthorized | enforced |

## Creation rule

The tag may be created only after RC1-T12 passes. The tag command must name the
full authorized target commit explicitly. Lightweight tags and moving an
existing tag are prohibited.

## GitHub pre-release rule

The GitHub pre-release may be created only after the remote annotated tag exists
and resolves exactly to the authorized target. The pre-release must not be
marked as the final/latest stable release.
