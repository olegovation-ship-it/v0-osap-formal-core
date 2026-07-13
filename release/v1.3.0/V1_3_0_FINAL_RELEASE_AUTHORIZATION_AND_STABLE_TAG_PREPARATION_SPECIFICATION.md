# V0 OSAP v1.3.0 Final Release Authorization and Stable-Tag Preparation Specification

**Patch version:** `0.1`  
**Date:** `2026-07-13`  
**Repository:** `olegovation-ship-it/v0-osap-formal-core`  
**Exact authorized stable target:** `13bf095688bcabd5b090f188e9bd28a16237edeb`  
**Stable tag candidate:** `v1.3.0`  
**State after patch:** `FINAL_RELEASE_AUTHORIZED / STABLE_TAG_NOT_CREATED / FINAL_GITHUB_RELEASE_NOT_CREATED / ZENODO_NOT_PUBLISHED`

## Purpose

This patch closes the authorization layer between the accepted RC1 publication-evidence
state and a future explicit stable-tag operation. It authorizes exactly one commit as the
stable release target and prepares deterministic tag/release material without executing
any publication action.

## Authorization basis

The exact target is PR #15's merge commit, which records the annotated RC1 tag
`v1.3.0-rc1`, exact RC1 target `cf9a05b46b9b6f29cd85942f99155f89a49817a7`, the published non-draft GitHub
pre-release, frozen RC1 manifests, restored executable gate-audit verification, and
post-merge evidence-closure CI.

## Release scope

- theorem range: `T121-T156`;
- theorem records: `36`;
- source crosswalks: `6`;
- conditional theorem records: `T140`, `T150`, `T156`;
- embedded checker component version: `0.7.0.dev1`.

The repository release identifier `v1.3.0` does not silently rewrite the embedded
checker component version. Any component-version promotion requires a separate audited
change and a separately authorized target.

## Execution boundary

After this patch is merged and all validation workflows pass, an operator may separately
create the annotated tag at the exact target, push that exact tag, and create a non-draft,
non-prerelease GitHub Release from the prepared notes. Zenodo publication and DOI mutation
remain outside this authorization.
