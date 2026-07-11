import V0OSAP.Prerequisites
import V0OSAP.DLE

namespace V0OSAP

def ListSubset (left right : List Id) : Prop :=
  ∀ item, item ∈ left → item ∈ right

def PrerequisiteClosed (step : Id → Id → Prop) (registers : List Id) : Prop :=
  ∀ target prerequisite, target ∈ registers → step target prerequisite → prerequisite ∈ registers

structure ClosureCertificate (step : Id → Id → Prop) (seed closure : List Id) : Prop where
  seedIncluded : ListSubset seed closure
  closed : PrerequisiteClosed step closure
  least : ∀ candidate, ListSubset seed candidate → PrerequisiteClosed step candidate → ListSubset closure candidate

theorem T127_closure_minimality
    (step : Id → Id → Prop) (seed closure candidate : List Id)
    (certificate : ClosureCertificate step seed closure)
    (hSeed : ListSubset seed candidate)
    (hClosed : PrerequisiteClosed step candidate) :
    ListSubset closure candidate :=
  certificate.least candidate hSeed hClosed

structure AlternativeSupportSelection
    (registry : RegistryState) (carrier context : Id) (family : PrerequisiteFamily) where
  selectedRegisterId : Id
  selectedMember : selectedRegisterId ∈ family.prerequisiteRegisterIds
  selectedLive : LiveGuard registry carrier selectedRegisterId context

theorem T128_alternative_support_transparency
    (registry : RegistryState) (carrier context : Id) (family : PrerequisiteFamily)
    (selection : AlternativeSupportSelection registry carrier context family) :
    selection.selectedRegisterId ∈ family.prerequisiteRegisterIds ∧
      LiveGuard registry carrier selection.selectedRegisterId context :=
  ⟨selection.selectedMember, selection.selectedLive⟩

structure CompatibilityConstraint where
  leftRegisterId : Id
  rightRegisterId : Id

def CompatibilityPreserved
    (registry : RegistryState) (carrier context : Id)
    (constraints : List CompatibilityConstraint) : Prop :=
  ∀ constraint, constraint ∈ constraints →
    ¬ (LiveGuard registry carrier constraint.leftRegisterId context ∧
       LiveGuard registry carrier constraint.rightRegisterId context)

theorem T129_compatibility_preservation
    (registry : RegistryState) (carrier context : Id)
    (constraints : List CompatibilityConstraint)
    (h : CompatibilityPreserved registry carrier context constraints) :
    ∀ constraint, constraint ∈ constraints →
      ¬ (LiveGuard registry carrier constraint.leftRegisterId context ∧
         LiveGuard registry carrier constraint.rightRegisterId context) := h

structure ProtocolRecord where
  protocolId : Id
  prerequisiteRegisterIds : List Id

def ProtocolReady
    (registry : RegistryState) (carrier context : Id) (protocol : ProtocolRecord) : Prop :=
  AllPrerequisitesLive registry carrier context protocol.prerequisiteRegisterIds

theorem T130_dimensional_readiness_soundness
    (registry : RegistryState) (carrier context : Id) (protocol : ProtocolRecord)
    (h : ProtocolReady registry carrier context protocol) :
    AllPrerequisitesLive registry carrier context protocol.prerequisiteRegisterIds := h

inductive DimensionResult where
  | undefinedDomain
  | readyValue (value : Int)
  deriving DecidableEq, Repr

theorem T131_undefined_is_not_zero :
    DimensionResult.undefinedDomain ≠ DimensionResult.readyValue 0 := by
  intro h
  cases h

theorem T132_dle_history_adequacy
    (registry : RegistryState) (carrier register context : Id)
    (h : DomainLicenseExhausted registry carrier register context) :
    WasLive registry carrier register context ∧ NoLive registry carrier register context := h

end V0OSAP
