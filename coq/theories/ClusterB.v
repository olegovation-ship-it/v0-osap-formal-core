From Coq Require Import String List.
From V0OSAP Require Import BasicTypes Registry Guards DLE Residuals Phase3 Phase4.
Import ListNotations.
Open Scope string_scope.

Record dle_transition : Type := mkDLETransition {
  transition_carrier_id : string;
  transition_register_id : string;
  transition_context_id : string
}.

Definition dle_transition_provenance
    (tr : dle_transition) (carrier register context : string) : Prop :=
  transition_carrier_id tr = carrier /\
  transition_register_id tr = register /\
  transition_context_id tr = context.

Definition strong_dle
    (registry : registry_state) (carrier register context : string)
    (tr : dle_transition) : Prop :=
  was_live registry carrier register context /\
  no_live registry carrier register context /\
  dle_transition_provenance tr carrier register context.

Theorem T157_strong_dle_characterization :
  forall registry carrier register context tr,
    strong_dle registry carrier register context tr <->
    was_live registry carrier register context /\
    no_live registry carrier register context /\
    dle_transition_provenance tr carrier register context.
Proof. reflexivity. Qed.

Record residual_ref : Type := mkResidualRef {
  residual_carrier_id : string;
  residual_register_id : string;
  residual_context_id : string
}.

Record residual_transition : Type := mkResidualTransition {
  transition_result : registry_state
}.

Definition apply_transition
    (tr : residual_transition) (_source : registry_state) : registry_state :=
  transition_result tr.

Definition noninterfering_dle
    (tr : residual_transition) (q : residual_ref) : Prop :=
  forall source,
    live_residual source
      (residual_carrier_id q) (residual_register_id q) (residual_context_id q) ->
    live_residual (transition_result tr)
      (residual_carrier_id q) (residual_register_id q) (residual_context_id q).

Theorem T158_live_residual_persistence_under_noninterfering_dle :
  forall R0 R1 q tr,
    live_residual R0
      (residual_carrier_id q) (residual_register_id q) (residual_context_id q) ->
    noninterfering_dle tr q ->
    apply_transition tr R0 = R1 ->
    live_residual R1
      (residual_carrier_id q) (residual_register_id q) (residual_context_id q).
Proof.
  intros R0 R1 q tr Hlive Hnon Hinter.
  unfold apply_transition in Hinter.
  subst R1.
  unfold noninterfering_dle in Hnon.
  exact (Hnon R0 Hlive).
Qed.

Inductive residual_kind : Type :=
| TargetPresence
| HistoricalResidual
| MemoryResidual
| SignalResidual
| CausalResidual
| InformationResidual
| GenericTraceResidual.

Record typed_residual : Type := mkTypedResidual {
  typed_residual_id : string;
  residual_type : residual_kind
}.

Definition admissible_translation (q1 q2 : typed_residual) : Prop :=
  typed_residual_id q1 = typed_residual_id q2.

Definition interchangeable (q1 q2 : typed_residual) : Prop :=
  residual_type q1 = residual_type q2 \/ admissible_translation q1 q2.

Theorem T159_residual_type_separation :
  forall q1 q2,
    residual_type q1 <> residual_type q2 ->
    ~ admissible_translation q1 q2 ->
    ~ interchangeable q1 q2.
Proof.
  intros q1 q2 Htypes Htranslation Hinterchangeable.
  destruct Hinterchangeable as [Hsame | Hmap].
  - apply Htypes. exact Hsame.
  - apply Htranslation. exact Hmap.
Qed.

Record cluster_b_model : Type := mkClusterBModel {
  cluster_model_id : string;
  shared_facts : list string;
  live_residual_ids : list string
}.

Definition admissible_model_pair
    (M1 M2 : cluster_b_model) (_shared_fragment : list string) : Prop :=
  cluster_model_id M1 <> cluster_model_id M2.

Definition agree_on
    (M1 M2 : cluster_b_model) (shared_fragment : list string) : Prop :=
  shared_facts M1 = shared_fragment /\ shared_facts M2 = shared_fragment.

Definition noneliminable_from (q : string) (shared_fragment : list string) : Prop :=
  exists M1 M2,
    admissible_model_pair M1 M2 shared_fragment /\
    agree_on M1 M2 shared_fragment /\
    (In q (live_residual_ids M1) <-> ~ In q (live_residual_ids M2)).

Theorem T160_model_pair_noneliminability_witness :
  forall M1 M2 shared_fragment q,
    admissible_model_pair M1 M2 shared_fragment ->
    agree_on M1 M2 shared_fragment ->
    (In q (live_residual_ids M1) <-> ~ In q (live_residual_ids M2)) ->
    noneliminable_from q shared_fragment.
Proof.
  intros M1 M2 shared_fragment q Hpair Hagree Hdifference.
  exists M1, M2.
  split.
  - exact Hpair.
  - split.
    + exact Hagree.
    + exact Hdifference.
Qed.

Definition declared_residual (q : string) (residual_registers : list string) : Prop :=
  In q residual_registers.

Definition minimal_obstruction_witness (_q : string) (claim : Prop) : Prop :=
  ~ claim.

Theorem T161_minimal_single_residual_obstruction :
  forall registry carrier context q residual_registers,
    declared_residual q residual_registers ->
    live_residual registry carrier q context ->
    minimal_obstruction_witness q
      (raw_relative_v0 registry carrier context residual_registers).
Proof.
  intros registry carrier context q residual_registers Hdeclared Hlive.
  unfold minimal_obstruction_witness.
  apply (T134_raw_residual_obstruction
    registry carrier context q residual_registers Hdeclared Hlive).
Qed.

Definition historical_token (token_value : token) : Prop :=
  partition token_value = Historical \/ partition token_value = Retired.

Definition current_live_guard_token (token_value : token) : Prop :=
  partition token_value = Live.

Definition fresh_activation (prior current : token) : Prop :=
  historical_token prior /\ current_live_guard_token current.

Theorem T162_historical_live_token_nonconversion :
  forall prior current,
    historical_token prior ->
    ~ fresh_activation prior current ->
    ~ current_live_guard_token current.
Proof.
  intros prior current Hhistorical Hnofresh Hcurrent.
  apply Hnofresh.
  split; assumption.
Qed.
