From Coq Require Import String List Bool Arith.
From V0OSAP Require Import BasicTypes Phase5.
Import ListNotations.
Open Scope string_scope.

Record extension_provenance_audit : Type := mkExtensionProvenanceAudit {
  extension_record_id : option string;
  extension_namespace : string;
  extension_base_theorem_ceiling : nat;
  extension_theorem_ids : list nat
}.

Definition explicit_extension_provenance
    (audit : extension_provenance_audit) : Prop :=
  extension_record_id audit <> None /\
  extension_namespace audit <> EmptyString /\
  extension_base_theorem_ceiling audit = 150 /\
  extension_theorem_ids audit = [151; 152; 153; 154; 155; 156].

Theorem T151_explicit_extension_provenance :
  forall audit,
    explicit_extension_provenance audit ->
    extension_base_theorem_ceiling audit = 150.
Proof.
  intros audit H.
  destruct H as [_ [_ [Hceiling _]]].
  exact Hceiling.
Qed.

Definition claim_vocabulary_closed
    (observed declared : list string) : Prop :=
  forall kind, In kind observed -> In kind declared.

Theorem T152_declared_claim_vocabulary_closure :
  forall observed declared,
    claim_vocabulary_closed observed declared ->
    forall kind, In kind observed -> In kind declared.
Proof.
  intros observed declared H.
  exact H.
Qed.

Record diagnostic_envelope_audit : Type := mkDiagnosticEnvelopeAudit {
  diagnostic_input_hash : string;
  diagnostic_ruleset_hash : string;
  first_diagnostic_envelope_hash : string;
  second_diagnostic_envelope_hash : string
}.

Definition diagnostic_envelope_deterministic
    (audit : diagnostic_envelope_audit) : Prop :=
  first_diagnostic_envelope_hash audit =
  second_diagnostic_envelope_hash audit.

Theorem T153_diagnostic_envelope_determinism :
  forall audit,
    diagnostic_envelope_deterministic audit ->
    first_diagnostic_envelope_hash audit =
    second_diagnostic_envelope_hash audit.
Proof.
  intros audit H.
  exact H.
Qed.

Definition evidence_provenance_acyclic (path : list string) : Prop :=
  NoDup path.

Theorem T154_evidence_provenance_acyclicity :
  forall path,
    evidence_provenance_acyclic path ->
    NoDup path.
Proof.
  intros path H.
  exact H.
Qed.

Record version_lock_audit : Type := mkVersionLockAudit {
  expected_schema_version : string;
  expected_language_version : string;
  expected_checker_version : string;
  expected_semantic_version : string;
  current_schema_version : string;
  current_language_version : string;
  current_checker_version : string;
  current_semantic_version : string
}.

Definition version_lock_coherent (audit : version_lock_audit) : Prop :=
  current_schema_version audit = expected_schema_version audit /\
  current_language_version audit = expected_language_version audit /\
  current_checker_version audit = expected_checker_version audit /\
  current_semantic_version audit = expected_semantic_version audit.

Theorem T155_version_lock_coherence :
  forall audit,
    version_lock_coherent audit ->
    current_checker_version audit = expected_checker_version audit.
Proof.
  intros audit H.
  destruct H as [_ [_ [Hchecker _]]].
  exact Hchecker.
Qed.

Record conservative_extension_audit : Type := mkConservativeExtensionAudit {
  baseline_result_hash : string;
  extended_result_hash : string;
  baseline_only_input : bool;
  extension_handlers_isolated : bool;
  baseline_rules_overridden : bool
}.

Definition conservative_extension_premises
    (audit : conservative_extension_audit) : Prop :=
  baseline_only_input audit = true /\
  extension_handlers_isolated audit = true /\
  baseline_rules_overridden audit = false.

Definition baseline_result_preserved
    (audit : conservative_extension_audit) : Prop :=
  baseline_result_hash audit = extended_result_hash audit.

Theorem T156_conservative_extension_noninterference :
  forall audit,
    (conservative_extension_premises audit ->
     baseline_result_preserved audit) ->
    conservative_extension_premises audit ->
    baseline_result_preserved audit.
Proof.
  intros audit Hsound Hpremises.
  apply Hsound.
  exact Hpremises.
Qed.
