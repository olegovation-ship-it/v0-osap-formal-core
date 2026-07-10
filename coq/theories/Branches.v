From Coq Require Import String.
Open Scope string_scope.

Record branch_claim : Type := mkBranchClaim {
  branch_claim_id : string;
  branch_id : string
}.

Record absolute_claim : Type := mkAbsoluteClaim {
  absolute_claim_id : string;
  source_claim_id : string
}.

Definition direct_promotion (local : branch_claim) (absolute : absolute_claim) : Prop :=
  source_claim_id absolute = branch_claim_id local.

Definition firewall_safe (local : branch_claim) (absolute : absolute_claim) : Prop :=
  ~ direct_promotion local absolute.

Theorem T126_direct_promotion_violates_firewall :
  forall local absolute,
    direct_promotion local absolute ->
    ~ firewall_safe local absolute.
Proof.
  intros local absolute Hpromotion Hsafe.
  apply Hsafe.
  exact Hpromotion.
Qed.
