From Coq Require Import String List Bool.
Import ListNotations.
Open Scope string_scope.

Inductive token_partition : Type :=
| Live
| Historical
| Retired
| Deferred.

Record token : Type := mkToken {
  token_id : string;
  carrier_id : string;
  register_id : string;
  context_id : string;
  partition : token_partition;
  introduced_in : string;
  source_evidence_id : string
}.

Inductive prerequisite_mode : Type :=
| AllOf
| OneOf.

Record prerequisite_family : Type := mkPrerequisiteFamily {
  family_id : string;
  target_register_id : string;
  mode : prerequisite_mode;
  prerequisite_register_ids : list string;
  family_enabled : bool
}.

Record claim : Type := mkClaim {
  claim_id : string;
  claim_kind : string
}.
