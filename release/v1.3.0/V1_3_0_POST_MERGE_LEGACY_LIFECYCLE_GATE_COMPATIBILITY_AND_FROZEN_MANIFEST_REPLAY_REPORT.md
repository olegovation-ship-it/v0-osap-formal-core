# V0 OSAP v1.3.0 Post-Merge Legacy Lifecycle Gate Compatibility and Frozen-Manifest Replay Report

## Diagnosis

PR #19 correctly records the post-merge archival closeout. The new archival workflow, Python checker, Lean 4, Coq, and schema validation pass. Nine older RC1/release workflows stop at the same legacy verifier before reaching their own later-stage checks.

The failing assertion in `scripts/verify_rc1_gate_audit.py` accepts lifecycle markers only through `DOI_FINALIZED`. The current README and status surfaces have legitimately advanced to:

`POST_MERGE_ARCHIVAL_CLOSEOUT_RECORDED / MAIN_DEVELOPMENT_SYNCHRONIZED / ZENODO_LIFECYCLE_REPLAY_COMPATIBLE / RELEASE_IMMUTABLE`.

The failure is therefore a compatibility defect in a historical gate surface, not a failure of the formal core or a reason to rewrite historical evidence.

## Repair

The patch extends the accepted lifecycle marker set with the four post-merge markers. It then adds a strict companion gate: whenever `POST_MERGE_ARCHIVAL_CLOSEOUT_RECORDED` is present, all three companion markers, the finalized v1.3.0 DOI, the exact stable-tag target, checker version `0.7.0.dev1`, and the conditional theorem identifiers T140, T150, and T156 must also be present.

This preserves monotonic lifecycle recognition without allowing a bare or under-evidenced post-merge marker to pass.

## Frozen evidence replay

The compatibility verifier checks eight previously frozen artifacts against the SHA-256 values already recorded in the Zenodo publication-evidence closure record and RC1 release-evidence closure record. Those artifacts are not regenerated and their recorded hashes are not replaced.

## Non-actions

The patch does not move `v1.3.0`, recreate or republish a GitHub Release, edit Zenodo, rebuild the archive, mutate either DOI, add theorem records, promote the checker, or remove the conditional status of T140, T150, or T156.

## Expected CI effect

The shared RC1 gate audit should pass, allowing the nine legacy workflows to proceed to their existing historical replay checks. Any later failure must be treated separately and must not be bypassed by weakening acceptance gates.
