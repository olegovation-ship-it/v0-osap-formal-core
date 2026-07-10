From Coq Require Import String List.
From V0OSAP Require Import BasicTypes.
Import ListNotations.
Open Scope string_scope.

Record registry_state : Type := mkRegistryState {
  state_id : string;
  registry_tokens : list token;
  registry_prerequisite_families : list prerequisite_family;
  registry_claims : list claim
}.

Definition token_matches
    (t : token) (carrier register context : string) : Prop :=
  carrier_id t = carrier /\ register_id t = register /\ context_id t = context.
