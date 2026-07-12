# V0 OSAP v1.1 Schema Errata — Phase 4

Status: `PHASE4_BUILD_READY / CI_PENDING`.

This erratum extends the development schema surface for T139-T144 without modifying the immutable v1.2.0 tag.

## Claim additions

| Claim kind | Required fields |
|---|---|
| `archive_guard_export` | `claim_id`, `archive_id`, `observer_id`, `register_id`, `context_id`, `exports_current_guard` |
| `external_witness_certificate` | `claim_id`, `observer_id`, `witness_id`, policy booleans, `external_evidence_ids`, `independence_group_ids` |
| `v0_branch_containment` | `claim_id`, `container_id`, `contained_branch_id`, `containment_mode` |
| `branch_distinctness` | branch IDs, labels, `distinctness_basis`, `evidence_ids` |
| `branch_cardinality` | `cardinality_kind`, `branch_ids`; non-finite kinds additionally require typed meta-index/evidence at semantic validation |
| `diagnostic_precedence_audit` | `diagnostic_statuses`, `expected_primary_status` |

## Semantic notes

- An archive is evidence, not a current guard source.
- Witness sufficiency is conditional on explicit non-circular policy fields.
- `ordinary` containment from a `NullMark` to a `Branch` is rejected.
- `label_only` is never a branch-distinctness proof.
- Missing non-finite cardinality licensing returns `DEFERRED_CARDINALITY_CERT`.
- Primary status is computed from the closed FC-1 status precedence.

This is a development erratum only and does not rewrite the v1.1 normative source or the archived v1.2.0 release.
