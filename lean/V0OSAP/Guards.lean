import V0OSAP.Registry

namespace V0OSAP


def LiveGuard (registry : RegistryState) (carrier register context : Id) : Prop :=
  ∃ token, token ∈ registry.tokens ∧ token.matches carrier register context ∧
    token.partition = TokenPartition.live


theorem liveGuard_has_live_token
    (registry : RegistryState) (carrier register context : Id)
    (h : LiveGuard registry carrier register context) :
    ∃ token, token ∈ registry.tokens ∧ token.matches carrier register context ∧
      token.partition = TokenPartition.live := h

end V0OSAP
