import V0OSAP.DLE

namespace V0OSAP


def LiveResidual (registry : RegistryState) (carrier residualRegister context : Id) : Prop :=
  LiveGuard registry carrier residualRegister context


def RobustRelativeV0
    (registry : RegistryState) (carrier targetRegister context : Id)
    (residualRegisters : List Id) : Prop :=
  DomainLicenseExhausted registry carrier targetRegister context ∧
    ∀ residualRegister, residualRegister ∈ residualRegisters →
      ¬ LiveResidual registry carrier residualRegister context


theorem live_residual_obstructs_robust_relative_v0
    (registry : RegistryState) (carrier targetRegister context residualRegister : Id)
    (residualRegisters : List Id)
    (hMember : residualRegister ∈ residualRegisters)
    (hLive : LiveResidual registry carrier residualRegister context) :
    ¬ RobustRelativeV0 registry carrier targetRegister context residualRegisters := by
  intro hRobust
  exact (hRobust.2 residualRegister hMember) hLive

end V0OSAP
