# V0 OSAP v1.3.0 Post-Merge Publication Lifecycle Replay and Frozen Zenodo Manifest Compatibility Report

## Context

The first compatibility repair removed the shared RC1 lifecycle blocker. The RC1 gate audit, RC1 release closure replay, RC1 tag authorization, RC1 evidence closure, release readiness, Python, Lean 4, Coq, schema validation, final-release authorization, and post-merge archival closeout all passed.

Three downstream workflows remained red for two distinct historical-replay reasons.

## Final-release evidence successor gate

The final-release evidence verifier replayed its historical evidence correctly but recognized successor states only through DOI finalization. The current repository has advanced to the guarded post-merge archival-closeout state.

The repair accepts `POST_MERGE_ARCHIVAL_CLOSEOUT_RECORDED` only when all companion markers, the exact stable target, both DOI boundaries, checker version `0.7.0.dev1`, and the conditional theorem ledger are present. A bare post-merge marker cannot pass.

## Frozen Zenodo manifest

The Zenodo publication-evidence builder originally regenerated its manifest from current files. That behavior is correct during initial publication closure but incorrect after archival closeout because README, changelog, and status surfaces have legitimately advanced.

The repaired builder detects the exact post-merge closeout record and enters historical replay mode. It requires the committed Zenodo manifest to remain byte-for-byte identical to the manifest at commit `53dcd231aa7d5208a2360d737f01bc2e95e9450b`. It does not rewrite the manifest.

The repaired verifier checks every frozen manifest entry against the corresponding blob in that snapshot, keeps immutable evidence files byte-identical, and separately validates the current post-merge successor surfaces.

## Preservation boundary

No tag is moved. No GitHub Release or Zenodo record is recreated, edited, or republished. No archive is rebuilt. Neither DOI is mutated. No historical manifest hash is replaced. No theorem is added. The checker remains `0.7.0.dev1`, and T140, T150, and T156 remain conditional.

## Expected CI result

The final-release evidence closure, Zenodo publication evidence closure, and post-Zenodo historical lifecycle replay workflows should pass while all previously green workflows remain green.
