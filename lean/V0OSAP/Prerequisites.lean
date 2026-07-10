import V0OSAP.Guards

namespace V0OSAP


def AllPrerequisitesLive
    (registry : RegistryState) (carrier context : Id) (registers : List Id) : Prop :=
  ∀ register, register ∈ registers → LiveGuard registry carrier register context


def OnePrerequisiteLive
    (registry : RegistryState) (carrier context : Id) (registers : List Id) : Prop :=
  ∃ register, register ∈ registers ∧ LiveGuard registry carrier register context


def FamilySatisfied
    (registry : RegistryState) (carrier context : Id) (family : PrerequisiteFamily) : Prop :=
  match family.mode with
  | PrerequisiteMode.allOf =>
      AllPrerequisitesLive registry carrier context family.prerequisiteRegisterIds
  | PrerequisiteMode.oneOf =>
      OnePrerequisiteLive registry carrier context family.prerequisiteRegisterIds


theorem empty_all_prerequisites_live
    (registry : RegistryState) (carrier context : Id) :
    AllPrerequisitesLive registry carrier context [] := by
  intro register h
  contradiction

end V0OSAP
