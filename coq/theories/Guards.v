From Coq Require Import String List.
From V0OSAP Require Import BasicTypes Registry.
Import ListNotations.
Open Scope string_scope.

Definition live_guard
    (registry : registry_state) (carrier register context : string) : Prop :=
  exists t,
    In t (registry_tokens registry) /\
    token_matches t carrier register context /\
    partition t = Live.

Theorem T121_live_guard_has_live_token :
  forall registry carrier register context,
    live_guard registry carrier register context ->
    exists t,
      In t (registry_tokens registry) /\
      token_matches t carrier register context /\
      partition t = Live.
Proof.
  intros registry carrier register context H.
  exact H.
Qed.
