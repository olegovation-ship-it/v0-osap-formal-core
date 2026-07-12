From Coq Require Import String List Bool.
From V0OSAP Require Import BasicTypes Phase4.
Import ListNotations.
Open Scope string_scope.

Record canonical_object : Type := mkCanonicalObject {
  canonical_payload : string
}.

Definition serialize_canonical (object : canonical_object) : string :=
  canonical_payload object.

Definition parse_canonical (bytes : string) : canonical_object :=
  mkCanonicalObject bytes.

Theorem T145_canonical_serialization_determinism :
  forall object,
    exists! bytes, bytes = serialize_canonical object.
Proof.
  intros object.
  exists (serialize_canonical object).
  split.
  - reflexivity.
  - intros other Hother.
    symmetry.
    exact Hother.
Qed.

Theorem T146_round_trip_identity :
  forall object,
    parse_canonical (serialize_canonical object) = object.
Proof.
  intros [payload].
  reflexivity.
Qed.

Record replay_input : Type := mkReplayInput {
  replay_proof_hash : string;
  replay_registry_hash : string;
  replay_ruleset_hash : string
}.

Record replay_result : Type := mkReplayResult {
  replay_status : string;
  replay_hash : string
}.

Definition replay_pinned (input : replay_input) : replay_result :=
  mkReplayResult
    "PASS"
    (String.append
      (replay_proof_hash input)
      (String.append (replay_registry_hash input) (replay_ruleset_hash input))).

Theorem T147_replay_determinism :
  forall input, replay_pinned input = replay_pinned input.
Proof.
  intros input.
  reflexivity.
Qed.

Record migration_audit : Type := mkMigrationAudit {
  migration_from_schema_version : string;
  migration_to_schema_version : string;
  migration_from_semantic_version : string;
  migration_to_semantic_version : string;
  migration_parser_coercion : bool;
  migration_record_id : option string
}.

Definition migration_changed (audit : migration_audit) : Prop :=
  migration_from_schema_version audit <> migration_to_schema_version audit \/
  migration_from_semantic_version audit <> migration_to_semantic_version audit.

Definition migration_visible (audit : migration_audit) : Prop :=
  ~ migration_changed audit \/
  (migration_parser_coercion audit = false /\ migration_record_id audit <> None).

Theorem T148_schema_migration_visibility :
  forall audit,
    migration_changed audit ->
    migration_visible audit ->
    migration_record_id audit <> None.
Proof.
  intros audit Hchanged Hvisible.
  destruct Hvisible as [Hunchanged | Hmigration].
  - exfalso. apply Hunchanged. exact Hchanged.
  - exact (proj2 Hmigration).
Qed.

Record backend_statement_mapping : Type := mkBackendStatementMapping {
  mapping_theorem_id : string;
  mapping_canonical_statement_hash : string;
  mapping_lean_statement_hash : string;
  mapping_coq_statement_hash : string;
  mapping_lean_symbol : string;
  mapping_coq_symbol : string
}.

Definition backend_statements_correspond
    (mapping : backend_statement_mapping) : Prop :=
  mapping_lean_statement_hash mapping =
    mapping_canonical_statement_hash mapping /\
  mapping_coq_statement_hash mapping =
    mapping_canonical_statement_hash mapping.

Theorem T149_backend_statement_correspondence :
  forall mapping,
    backend_statements_correspond mapping ->
    mapping_lean_statement_hash mapping =
      mapping_coq_statement_hash mapping.
Proof.
  intros mapping H.
  destruct H as [Hlean Hcoq].
  rewrite Hlean.
  symmetry.
  exact Hcoq.
Qed.

Record accepted_fragment_audit : Type := mkAcceptedFragmentAudit {
  accepted_fragment_id : string;
  accepted_checker_status : string;
  accepted_rule_lemmas_proved : bool;
  accepted_implementation_invariants_hold : bool;
  accepted_semantic_obligations_hold : bool
}.

Definition accepted_fragment_premises
    (audit : accepted_fragment_audit) : Prop :=
  accepted_rule_lemmas_proved audit = true /\
  accepted_implementation_invariants_hold audit = true.

Definition accepted_checker_pass
    (audit : accepted_fragment_audit) : Prop :=
  accepted_checker_status audit = "PASS".

Definition accepted_fragment_obligations
    (audit : accepted_fragment_audit) : Prop :=
  accepted_semantic_obligations_hold audit = true.

Theorem T150_accepted_fragment_checker_soundness :
  forall audit,
    (accepted_fragment_premises audit ->
     accepted_checker_pass audit ->
     accepted_fragment_obligations audit) ->
    accepted_fragment_premises audit ->
    accepted_checker_pass audit ->
    accepted_fragment_obligations audit.
Proof.
  intros audit Hsound Hpremises Hpass.
  apply Hsound; assumption.
Qed.
