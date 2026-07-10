import V0OSAP.BasicTypes

namespace V0OSAP

structure BranchClaim where
  claimId : Id
  branchId : Id
  deriving DecidableEq, Repr

structure AbsoluteClaim where
  claimId : Id
  sourceClaimId : Id
  deriving DecidableEq, Repr


def DirectPromotion (local : BranchClaim) (absolute : AbsoluteClaim) : Prop :=
  absolute.sourceClaimId = local.claimId


def FirewallSafe (local : BranchClaim) (absolute : AbsoluteClaim) : Prop :=
  ¬ DirectPromotion local absolute


theorem direct_promotion_violates_firewall
    (local : BranchClaim) (absolute : AbsoluteClaim)
    (h : DirectPromotion local absolute) :
    ¬ FirewallSafe local absolute := by
  intro hSafe
  exact hSafe h

end V0OSAP
