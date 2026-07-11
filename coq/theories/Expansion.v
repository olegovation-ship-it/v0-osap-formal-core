From Coq Require Import String List ZArith.
From V0OSAP Require Import BasicTypes Registry Guards Prerequisites DLE.
Import ListNotations.
Open Scope string_scope.
Open Scope Z_scope.

Definition list_subset (left right : list string) : Prop :=
  forall item, In item left -> In item right.

Definition prerequisite_closed (step : string -> string -> Prop) (registers : list string) : Prop :=
  forall target prerequisite, In target registers -> step target prerequisite -> In prerequisite registers.

Definition closure_certificate (step : string -> string -> Prop) (seed closure : list string) : Prop :=
  list_subset seed closure /\ prerequisite_closed step closure /\
  forall candidate, list_subset seed candidate -> prerequisite_closed step candidate -> list_subset closure candidate.

Theorem T127_closure_minimality :
  forall step seed closure candidate,
    closure_certificate step seed closure -> list_subset seed candidate ->
    prerequisite_closed step candidate -> list_subset closure candidate.
Proof. intros step seed closure candidate Hcert Hseed Hclosed. destruct Hcert as [_ [_ Hleast]]. exact (Hleast candidate Hseed Hclosed). Qed.

Theorem T128_alternative_support_transparency :
  forall registry carrier context prerequisites selected,
    In selected prerequisites -> live_guard registry carrier selected context ->
    In selected prerequisites /\ live_guard registry carrier selected context.
Proof. intros. split; assumption. Qed.

Record compatibility_constraint := { left_register_id : string; right_register_id : string }.
Definition compatibility_preserved (registry : registry_state) (carrier context : string)
    (constraints : list compatibility_constraint) : Prop :=
  forall constraint, In constraint constraints ->
    ~ (live_guard registry carrier (left_register_id constraint) context /\
       live_guard registry carrier (right_register_id constraint) context).

Theorem T129_compatibility_preservation :
  forall registry carrier context constraints,
    compatibility_preserved registry carrier context constraints ->
    forall constraint, In constraint constraints ->
      ~ (live_guard registry carrier (left_register_id constraint) context /\
         live_guard registry carrier (right_register_id constraint) context).
Proof. intros registry carrier context constraints H constraint Hin. exact (H constraint Hin). Qed.

Record protocol_record := { protocol_id : string; protocol_prerequisite_register_ids : list string }.
Definition protocol_ready (registry : registry_state) (carrier context : string) (protocol : protocol_record) : Prop :=
  all_prerequisites_live registry carrier context (protocol_prerequisite_register_ids protocol).

Theorem T130_dimensional_readiness_soundness :
  forall registry carrier context protocol,
    protocol_ready registry carrier context protocol ->
    all_prerequisites_live registry carrier context (protocol_prerequisite_register_ids protocol).
Proof. intros. exact H. Qed.

Inductive dimension_result : Type := UndefinedDomain | ReadyValue (value : Z).
Theorem T131_undefined_is_not_zero : UndefinedDomain <> ReadyValue 0.
Proof. discriminate. Qed.

Theorem T132_dle_history_adequacy :
  forall registry carrier register context,
    domain_license_exhausted registry carrier register context ->
    was_live registry carrier register context /\ no_live registry carrier register context.
Proof. intros. exact H. Qed.
