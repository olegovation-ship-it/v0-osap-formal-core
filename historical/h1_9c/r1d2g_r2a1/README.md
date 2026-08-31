# H1.9C-R1d2g-R2A1 — implementation only

This directory implements the frozen R2A0 resource-exhaustion closure contract without executing the six real-domain scientific IDs.

## Frozen implementation properties

- exact simple-path enumeration is streamed rather than returned as an eager chain list;
- start/end source anchors are losslessly indexed by `backbone_id`;
- mapping objects are transient and canonicalized immediately;
- canonical records are sorted/deduplicated through bounded-memory disk chunks and deterministic k-way merge;
- the legacy `M_` 128-bit SHA-256 prefix remains a compatibility label, while canonical-byte equality plus full SHA-256 provide collision-safe identity;
- prefix collision fails closed;
- any state/time/disk guard hit routes to `NOT_REACHED_RESOURCE_EXHAUSTION`, never to an empty scientific set;
- FX and I are compared only after both C14b results are PASS;
- SHA manifests explicitly exclude themselves.

R2A1 is **implementation only**. No target/CMB access, shaft-vector extraction, AUC/PI, synthetic rotations, significance claims, mapping promotion, or geometry promotion is authorized here.

Controlling R2A0 contract hashes:

- Markdown SHA-256: `429e68e9d28cd271f3a19b93b514cffc88e10ccc6423b02a1080e1546f4e3282`
- JSON SHA-256: `564eb174de2b59c25d852195508abc7f81403e2f6175ef7190816995881ae092`
