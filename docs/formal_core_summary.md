# FC-1 formal-core summary

FC-1 is a finite registry fragment. It separates four token partitions and evaluates only claims whose registry, context, carrier, register, and evidence references are declared.

The bootstrap checker implements a conservative subset:

1. declaration, token, family, and claim identifiers are unique;
2. references from tokens and prerequisite families resolve;
3. a value claim requires a matching live token;
4. a DLE claim requires historical evidence and current non-liveness;
5. every enabled prerequisite family for a live target token must be satisfied;
6. a relative-V0 claim cannot be used as direct support for an absolute-V0 claim;
7. an observer terminal self-certificate requires independent external support;
8. deterministic diagnostics are sorted by priority, code, and instance path.

Schema validity is necessary but not sufficient for semantic acceptance.
