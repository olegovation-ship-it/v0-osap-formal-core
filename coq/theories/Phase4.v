
From Coq Require Import String List Bool Arith.
From V0OSAP Require Import BasicTypes Observer Branches.
Import ListNotations.
Open Scope string_scope.

Record archive_guard_export : Type := mkArchiveGuardExport {
  archive_id_p4 : string;
  archive_observer_id : string;
  archive_register_id : string;
  archive_context_id : string;
  exports_current_guard : bool
}.

Definition archive_non_guard_export (record : archive_guard_export) : Prop :=
  exports_current_guard record = false.

Theorem T139_archive_non_guard_export :
  forall record,
    archive_non_guard_export record ->
    exports_current_guard record = false.
Proof.
  intros record H.
  exact H.
Qed.


Record independent_witness_certificate : Type := mkIndependentWitnessCertificate {
  witness_id_p4 : string;
  witness_observer_id : string;
  policy_compliant : bool;
  non_circular : bool;
  identity_verified : bool;
  evidence_verified : bool;
  witness_external_evidence_ids : list string;
  witness_independence_group_ids : list string
}.

Definition independent_witness_admissible
    (certificate : independent_witness_certificate) : Prop :=
  policy_compliant certificate = true /\
  non_circular certificate = true /\
  identity_verified certificate = true /\
  evidence_verified certificate = true /\
  witness_external_evidence_ids certificate <> [] /\
  witness_independence_group_ids certificate <> [].

Definition external_certificate_supported
    (certificate : independent_witness_certificate) : Prop :=
  witness_external_evidence_ids certificate <> [] /\
  witness_independence_group_ids certificate <> [].

Theorem T140_independent_witness_conditional_sufficiency :
  forall certificate,
    independent_witness_admissible certificate ->
    external_certificate_supported certificate.
Proof.
  intros certificate H.
  destruct H as [_ [_ [_ [_ [Hexternal Hindependent]]]]].
  split; assumption.
Qed.


Inductive containment_mode : Type :=
| ContainmentNone
| ContainmentOrdinary
| ContainmentTypedMeta.

Record v0_branch_containment : Type := mkV0BranchContainment {
  containment_container_id : string;
  containment_branch_id : string;
  containment_mode_value : containment_mode
}.

Definition no_ordinary_container (record : v0_branch_containment) : Prop :=
  containment_mode_value record <> ContainmentOrdinary.

Theorem T141_no_container :
  forall record,
    containment_mode_value record = ContainmentOrdinary ->
    ~ no_ordinary_container record.
Proof.
  intros record Hordinary Hno.
  apply Hno.
  exact Hordinary.
Qed.


Inductive distinctness_basis : Type :=
| BasisLabelOnly
| BasisNonIsomorphism
| BasisIncompatibleProfile
| BasisObservationalSeparation
| BasisRegisteredPolicy.

Record branch_distinctness_certificate : Type := mkBranchDistinctnessCertificate {
  distinct_left_branch_id : string;
  distinct_right_branch_id : string;
  distinct_left_label : string;
  distinct_right_label : string;
  distinct_basis : distinctness_basis;
  distinct_evidence_ids : list string
}.

Definition label_independent_distinctness
    (certificate : branch_distinctness_certificate) : Prop :=
  distinct_basis certificate <> BasisLabelOnly.

Theorem T142_branch_label_insufficiency :
  forall certificate,
    distinct_basis certificate = BasisLabelOnly ->
    ~ label_independent_distinctness certificate.
Proof.
  intros certificate Hlabel Hdistinct.
  apply Hdistinct.
  exact Hlabel.
Qed.


Inductive cardinality_kind : Type :=
| CardinalityFiniteEnumerated
| CardinalityCountable
| CardinalityUncountable
| CardinalityProperClass.

Record cardinality_certificate : Type := mkCardinalityCertificate {
  cardinality_kind_value : cardinality_kind;
  cardinality_meta_index_id : option string;
  cardinality_evidence_ids : list string
}.

Definition nonfinite_kind (certificate : cardinality_certificate) : Prop :=
  cardinality_kind_value certificate <> CardinalityFiniteEnumerated.

Definition cardinality_licensed (certificate : cardinality_certificate) : Prop :=
  cardinality_kind_value certificate = CardinalityFiniteEnumerated \/
  (cardinality_kind_value certificate <> CardinalityFiniteEnumerated /\
   exists index_id,
     cardinality_meta_index_id certificate = Some index_id /\
     cardinality_evidence_ids certificate <> []).

Theorem T143_cardinality_licensing :
  forall certificate,
    nonfinite_kind certificate ->
    cardinality_licensed certificate ->
    exists index_id,
      cardinality_meta_index_id certificate = Some index_id /\
      cardinality_evidence_ids certificate <> [].
Proof.
  intros certificate Hnonfinite Hlicensed.
  destruct Hlicensed as [Hfinite | Hlicensed].
  - exfalso. apply Hnonfinite. exact Hfinite.
  - exact (proj2 Hlicensed).
Qed.


Inductive diagnostic_status : Type :=
| StatusPass
| StatusOutOfScope
| StatusIndeterminate
| StatusDeferred
| StatusReject.

Definition diagnostic_status_rank (status : diagnostic_status) : nat :=
  match status with
  | StatusPass => 0
  | StatusOutOfScope => 1
  | StatusIndeterminate => 2
  | StatusDeferred => 3
  | StatusReject => 4
  end.

Definition choose_primary_status
    (current candidate : diagnostic_status) : diagnostic_status :=
  if Nat.leb (diagnostic_status_rank current) (diagnostic_status_rank candidate)
  then candidate
  else current.

Definition primary_status (statuses : list diagnostic_status) : diagnostic_status :=
  match statuses with
  | [] => StatusPass
  | head :: tail => fold_left choose_primary_status tail head
  end.

Theorem T144_diagnostic_precedence_totality :
  forall statuses,
    exists! primary, primary = primary_status statuses.
Proof.
  intros statuses.
  exists (primary_status statuses).
  split.
  - reflexivity.
  - intros other Hother.
    symmetry.
    exact Hother.
Qed.
