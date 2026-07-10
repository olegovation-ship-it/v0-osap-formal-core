From Coq Require Import String List.
From V0OSAP Require Import Registry Guards.
Import ListNotations.
Open Scope string_scope.

Definition all_prerequisites_live
    (registry : registry_state) (carrier context : string) (registers : list string) : Prop :=
  forall register, In register registers -> live_guard registry carrier register context.

Definition one_prerequisite_live
    (registry : registry_state) (carrier context : string) (registers : list string) : Prop :=
  exists register, In register registers /\ live_guard registry carrier register context.

Theorem T122_empty_all_prerequisites_live :
  forall registry carrier context,
    all_prerequisites_live registry carrier context [].
Proof.
  intros registry carrier context register H.
  inversion H.
Qed.
