From Coq Require Import String List.
Import ListNotations.
Open Scope string_scope.

Record observer_support : Type := mkObserverSupport {
  observer_id : string;
  internal_support_ids : list string;
  external_evidence_ids : list string;
  independence_group_ids : list string
}.

Definition terminal_self_certificate (support : observer_support) : Prop :=
  internal_support_ids support = [] /\ external_evidence_ids support = [].

Theorem T125_terminal_self_certificate_exposes_empty_support :
  forall support,
    terminal_self_certificate support ->
    internal_support_ids support = [] /\ external_evidence_ids support = [].
Proof.
  intros support H.
  exact H.
Qed.
