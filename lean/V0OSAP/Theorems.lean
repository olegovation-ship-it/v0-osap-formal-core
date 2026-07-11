import V0OSAP.Guards
import V0OSAP.Prerequisites
import V0OSAP.DLE
import V0OSAP.Residuals
import V0OSAP.Observer
import V0OSAP.Branches
import V0OSAP.Expansion

namespace V0OSAP


theorem T121
    (registry : RegistryState) (carrier register context : Id)
    (h : LiveGuard registry carrier register context) :
    ∃ token, token ∈ registry.tokens ∧ token.matches carrier register context ∧
      token.partition = TokenPartition.live :=
  liveGuard_has_live_token registry carrier register context h


theorem T122
    (registry : RegistryState) (carrier context : Id) :
    AllPrerequisitesLive registry carrier context [] :=
  empty_all_prerequisites_live registry carrier context


theorem T123
    (registry : RegistryState) (carrier register context : Id)
    (h : DomainLicenseExhausted registry carrier register context) :
    NoLive registry carrier register context :=
  dle_implies_no_live registry carrier register context h


theorem T124
    (registry : RegistryState) (carrier targetRegister context residualRegister : Id)
    (residualRegisters : List Id)
    (hMember : residualRegister ∈ residualRegisters)
    (hLive : LiveResidual registry carrier residualRegister context) :
    ¬ RobustRelativeV0 registry carrier targetRegister context residualRegisters :=
  live_residual_obstructs_robust_relative_v0
    registry carrier targetRegister context residualRegister residualRegisters hMember hLive


theorem T125
    (support : ObserverSupport) (h : TerminalSelfCertificate support) :
    support.internalSupportIds = [] ∧ support.externalEvidenceIds = [] :=
  terminal_self_certificate_exposes_empty_support support h


theorem T126
    (branchClaim : BranchClaim) (absoluteClaim : AbsoluteClaim)
    (h : DirectPromotion branchClaim absoluteClaim) :
    ¬ FirewallSafe branchClaim absoluteClaim :=
  direct_promotion_violates_firewall branchClaim absoluteClaim h

end V0OSAP
