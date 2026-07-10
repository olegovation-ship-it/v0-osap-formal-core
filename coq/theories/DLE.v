From Coq Require Import String List.
From V0OSAP Require Import BasicTypes Registry Guards.
Import ListNotations.
Open Scope string_scope.

Definition was_live
    (registry : registry_state) (carrier register context : string) : Prop :=
  exists t,
    In t (registry_tokens registry) /\
    token_matches t carrier register context /\
    (partition t = Historical \/ partition t = Retired).

Definition no_live
    (registry : registry_state) (carrier register context : string) : Prop :=
  ~ live_guard registry carrier register context.

Definition domain_license_exhausted
    (registry : registry_state) (carrier register context : string) : Prop :=
  was_live registry carrier register context /\
  no_live registry carrier register context.

Theorem T123_dle_implies_no_live :
  forall registry carrier register context,
    domain_license_exhausted registry carrier register context ->
    no_live registry carrier register context.
Proof.
  intros registry carrier register context H.
  destruct H as [_ Hno].
  exact Hno.
Qed.
