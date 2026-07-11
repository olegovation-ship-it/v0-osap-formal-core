From Coq Require Import String List.
From V0OSAP Require Import BasicTypes Registry Guards DLE Residuals Observer Branches.
Import ListNotations.
Open Scope string_scope.

Definition fresh_token_reactivation
    (registry : registry_state) (prior reactivated : token) : Prop :=
  In prior (registry_tokens registry) /\
  In reactivated (registry_tokens registry) /\
  (partition prior = Historical \/ partition prior = Retired) /\
  partition reactivated = Live /\
  carrier_id prior = carrier_id reactivated /\
  register_id prior = register_id reactivated /\
  context_id prior = context_id reactivated /\
  token_id reactivated <> token_id prior.

Theorem T133_fresh_token_reactivation :
  forall registry prior reactivated,
    fresh_token_reactivation registry prior reactivated ->
    token_id reactivated <> token_id prior.
Proof.
  intros registry prior reactivated H.
  destruct H as [_ [_ [_ [_ [_ [_ [_ Hfresh]]]]]]].
  exact Hfresh.
Qed.

Definition raw_relative_v0
    (registry : registry_state) (carrier context : string)
    (residual_registers : list string) : Prop :=
  forall residual_register,
    In residual_register residual_registers ->
    ~ live_residual registry carrier residual_register context.

Theorem T134_raw_residual_obstruction :
  forall registry carrier context residual_register residual_registers,
    In residual_register residual_registers ->
    live_residual registry carrier residual_register context ->
    ~ raw_relative_v0 registry carrier context residual_registers.
Proof.
  intros registry carrier context residual_register residual_registers Hmem Hlive Hraw.
  apply (Hraw residual_register Hmem).
  exact Hlive.
Qed.

Definition robust_relative_v0_noneliminable
    (registry : registry_state) (carrier target_register context : string)
    (noneliminable_residual_registers : list string) : Prop :=
  domain_license_exhausted registry carrier target_register context /\
  forall residual_register,
    In residual_register noneliminable_residual_registers ->
    ~ live_residual registry carrier residual_register context.

Theorem T135_robust_residual_obstruction :
  forall registry carrier target_register context residual_register residual_registers,
    In residual_register residual_registers ->
    live_residual registry carrier residual_register context ->
    ~ robust_relative_v0_noneliminable registry carrier target_register context residual_registers.
Proof.
  intros registry carrier target_register context residual_register residual_registers Hmem Hlive Hrobust.
  destruct Hrobust as [_ Hnone].
  apply (Hnone residual_register Hmem).
  exact Hlive.
Qed.

Inductive v0_claim_tier : Type :=
| RelativeTier
| AbsoluteTier
| ApproximationTier
| IdentityTier.

Theorem T136_relative_to_absolute_non_promotion :
  RelativeTier <> AbsoluteTier.
Proof. discriminate. Qed.

Theorem T137_approximation_non_identity :
  ApproximationTier <> IdentityTier.
Proof. discriminate. Qed.

Record terminal_exhaustion_certificate : Type := mkTerminalExhaustionCertificate {
  support_state_id : string;
  certification_state_id : string
}.

Definition terminal_exhaustion_admissible
    (certificate : terminal_exhaustion_certificate) : Prop :=
  support_state_id certificate <> certification_state_id certificate.

Theorem T138_terminal_self_certification_limit :
  forall certificate,
    support_state_id certificate = certification_state_id certificate ->
    ~ terminal_exhaustion_admissible certificate.
Proof.
  intros certificate Hsame Hadmissible.
  apply Hadmissible.
  exact Hsame.
Qed.
