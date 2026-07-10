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

def DirectPromotion
    (branchClaim : BranchClaim)
    (absoluteClaim : AbsoluteClaim) : Prop :=
  absoluteClaim.sourceClaimId = branchClaim.claimId

def FirewallSafe
    (branchClaim : BranchClaim)
    (absoluteClaim : AbsoluteClaim) : Prop :=
  ¬ DirectPromotion branchClaim absoluteClaim

theorem direct_promotion_violates_firewall
    (branchClaim : BranchClaim)
    (absoluteClaim : AbsoluteClaim)
    (h : DirectPromotion branchClaim absoluteClaim) :
    ¬ FirewallSafe branchClaim absoluteClaim := by
  intro hSafe
  exact hSafe h

end V0OSAP
