import V0OSAP.Guards

namespace V0OSAP


def WasLive (registry : RegistryState) (carrier register context : Id) : Prop :=
  ∃ token, token ∈ registry.tokens ∧ token.matches carrier register context ∧
    (token.partition = TokenPartition.historical ∨ token.partition = TokenPartition.retired)


def NoLive (registry : RegistryState) (carrier register context : Id) : Prop :=
  ¬ LiveGuard registry carrier register context


def DomainLicenseExhausted
    (registry : RegistryState) (carrier register context : Id) : Prop :=
  WasLive registry carrier register context ∧ NoLive registry carrier register context


theorem dle_implies_no_live
    (registry : RegistryState) (carrier register context : Id)
    (h : DomainLicenseExhausted registry carrier register context) :
    NoLive registry carrier register context := h.2

end V0OSAP
