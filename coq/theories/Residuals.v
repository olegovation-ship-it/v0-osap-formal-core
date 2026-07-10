From Coq Require Import String List.
From V0OSAP Require Import Registry Guards DLE.
Import ListNotations.
Open Scope string_scope.

Definition live_residual
    (registry : registry_state) (carrier residual_register context : string) : Prop :=
  live_guard registry carrier residual_register context.

Definition robust_relative_v0
    (registry : registry_state) (carrier target_register context : string)
    (residual_registers : list string) : Prop :=
  domain_license_exhausted registry carrier target_register context /\
  forall residual_register,
    In residual_register residual_registers ->
    ~ live_residual registry carrier residual_register context.

Theorem T124_live_residual_obstructs_robust_relative_v0 :
  forall registry carrier target_register context residual_register residual_registers,
    In residual_register residual_registers ->
    live_residual registry carrier residual_register context ->
    ~ robust_relative_v0 registry carrier target_register context residual_registers.
Proof.
  intros registry carrier target_register context residual_register residual_registers Hmem Hlive Hrobust.
  destruct Hrobust as [_ Hnone].
  apply (Hnone residual_register Hmem).
  exact Hlive.
Qed.
