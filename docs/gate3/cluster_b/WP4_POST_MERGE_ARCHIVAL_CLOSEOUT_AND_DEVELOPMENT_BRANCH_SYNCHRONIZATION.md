# Gate 3 Cluster B WP4 Post-Merge Archival Closeout and Development-Branch Synchronization

## Canonical identity

- Repository: `olegovation-ship-it/v0-osap-formal-core`
- Source PR: `#27`
- Accepted WP4 head: `633c01e33271ffb17c045f69aa266a595ebc7e74`
- Canonical WP4 merge commit: `cdae3ea4e50f6222182f2398c350476fbe820f92`
- Pre-WP4 baseline: `c90041d3da5b680b574b910de50d8769d32fbfa9`
- Hosted checks before merge: `25/25 PASS`
- Branch relation at capture: `origin/main` is one merge commit ahead of `origin/v1.4.0-development`.
- Working tree at capture: clean.

## Closeout scope

This surface archives the completed WP4 Lean/Coq proof-completion and statement-parity lifecycle,
records the merge and hosted-CI evidence, installs a bounded successor SHA-256 ledger,
and provides a separately invoked fast-forward synchronization script for the development branch.

The closeout does not change theorem identities T157-T162, proof statements, statement hashes,
proof bodies, activation semantics, typed outcomes, fixtures, or canonical WP4 release records.
It does not authorize WP5.

## Preservation firewall

Canonical WP0/WP1/WP2/WP3/WP4 records and canonical ledgers remain byte-preserved.
Only these successor-control files are replaced under exact path and hash control:

- `release/v1.4.0/tools/patch_wp4_allowlist.py`
- `scripts/build_gate3_cluster_b_wp4.py`
- `scripts/verify_gate3_cluster_b_wp4.py`

All other closeout paths are additive. The canonical WP4 ledger remains unchanged; the new
successor ledger attests the three controlled replacements and the additive closeout surfaces.

## Authorization boundary

The applicator never commits or pushes. No release tag, GitHub Release, Zenodo publication,
DOI creation or mutation, force-push, history rewrite, branch deletion, or automatic WP5 start
is authorized.

## Lifecycle after package application

1. Run the applicator with `--check`; it validates the payload in a disposable worktree.
2. Run the applicator without `--check`; inspect the exact 23-path working-tree delta.
3. Commit and push manually on `v1.4.0-development`.
4. Open a dedicated WP4 post-merge closeout PR to `main`.
5. Merge only after every hosted check succeeds, using a normal merge commit.
6. Invoke `scripts/synchronize_v1_4_0_development_wp4.sh` explicitly.
7. Confirm `origin/main == origin/v1.4.0-development`, divergence `0 0`, and a clean tree.
8. Begin WP5 only under a separate build specification and implementation authorization.
