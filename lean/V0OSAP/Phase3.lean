import V0OSAP.Residuals
import V0OSAP.Observer
import V0OSAP.Branches

namespace V0OSAP


def FreshTokenReactivation
    (registry : RegistryState) (priorToken reactivatedToken : Token) : Prop :=
  priorToken ∈ registry.tokens ∧
  reactivatedToken ∈ registry.tokens ∧
  (priorToken.partition = TokenPartition.historical ∨
    priorToken.partition = TokenPartition.retired) ∧
  reactivatedToken.partition = TokenPartition.live ∧
  priorToken.carrierId = reactivatedToken.carrierId ∧
  priorToken.registerId = reactivatedToken.registerId ∧
  priorToken.contextId = reactivatedToken.contextId ∧
  reactivatedToken.tokenId ≠ priorToken.tokenId


theorem T133_fresh_token_reactivation
    (registry : RegistryState) (priorToken reactivatedToken : Token)
    (h : FreshTokenReactivation registry priorToken reactivatedToken) :
    reactivatedToken.tokenId ≠ priorToken.tokenId := by
  rcases h with ⟨_, _, _, _, _, _, _, hFresh⟩
  exact hFresh


def RawRelativeV0
    (registry : RegistryState) (carrier context : Id)
    (residualRegisters : List Id) : Prop :=
  ∀ residualRegister, residualRegister ∈ residualRegisters →
    ¬ LiveResidual registry carrier residualRegister context


theorem T134_raw_residual_obstruction
    (registry : RegistryState) (carrier context residualRegister : Id)
    (residualRegisters : List Id)
    (hMember : residualRegister ∈ residualRegisters)
    (hLive : LiveResidual registry carrier residualRegister context) :
    ¬ RawRelativeV0 registry carrier context residualRegisters := by
  intro hRaw
  exact (hRaw residualRegister hMember) hLive


def RobustRelativeV0NonEliminable
    (registry : RegistryState) (carrier targetRegister context : Id)
    (nonEliminableResidualRegisters : List Id) : Prop :=
  DomainLicenseExhausted registry carrier targetRegister context ∧
  ∀ residualRegister, residualRegister ∈ nonEliminableResidualRegisters →
    ¬ LiveResidual registry carrier residualRegister context


theorem T135_robust_residual_obstruction
    (registry : RegistryState) (carrier targetRegister context residualRegister : Id)
    (nonEliminableResidualRegisters : List Id)
    (hMember : residualRegister ∈ nonEliminableResidualRegisters)
    (hLive : LiveResidual registry carrier residualRegister context) :
    ¬ RobustRelativeV0NonEliminable registry carrier targetRegister context
      nonEliminableResidualRegisters := by
  intro hRobust
  exact (hRobust.2 residualRegister hMember) hLive


inductive V0ClaimTier where
  | relative
  | absolute
  | approximation
  | identity
  deriving DecidableEq, Repr


theorem T136_relative_to_absolute_non_promotion :
    V0ClaimTier.relative ≠ V0ClaimTier.absolute := by
  decide


theorem T137_approximation_non_identity :
    V0ClaimTier.approximation ≠ V0ClaimTier.identity := by
  decide


structure TerminalExhaustionCertificate where
  supportStateId : Id
  certificationStateId : Id
  deriving DecidableEq, Repr


def TerminalExhaustionAdmissible
    (certificate : TerminalExhaustionCertificate) : Prop :=
  certificate.supportStateId ≠ certificate.certificationStateId


theorem T138_terminal_self_certification_limit
    (certificate : TerminalExhaustionCertificate)
    (hSameState : certificate.supportStateId = certificate.certificationStateId) :
    ¬ TerminalExhaustionAdmissible certificate := by
  intro hAdmissible
  exact hAdmissible hSameState

end V0OSAP
