import V0OSAP.DLE
import V0OSAP.Residuals
import V0OSAP.Phase3
import V0OSAP.Phase4

namespace V0OSAP

structure DLETransition where
  carrierId : Id
  registerId : Id
  contextId : Id
  deriving DecidableEq, Repr

def DLETransitionProvenance
    (tr : DLETransition) (carrier register context : Id) : Prop :=
  tr.carrierId = carrier ∧ tr.registerId = register ∧ tr.contextId = context

def StrongDLE
    (registry : RegistryState) (carrier register context : Id)
    (tr : DLETransition) : Prop :=
  WasLive registry carrier register context ∧
  NoLive registry carrier register context ∧
  DLETransitionProvenance tr carrier register context

theorem T157_strong_dle_characterization
    (registry : RegistryState) (carrier register context : Id)
    (tr : DLETransition) :
    StrongDLE registry carrier register context tr ↔
      WasLive registry carrier register context ∧
      NoLive registry carrier register context ∧
      DLETransitionProvenance tr carrier register context := by
  rfl

structure ResidualRef where
  carrierId : Id
  registerId : Id
  contextId : Id
  deriving DecidableEq, Repr

structure ResidualTransition where
  result : RegistryState
  deriving Repr

def Apply (tr : ResidualTransition) (_source : RegistryState) : RegistryState :=
  tr.result

def NonInterferingDLE (tr : ResidualTransition) (q : ResidualRef) : Prop :=
  ∀ source : RegistryState,
    LiveResidual source q.carrierId q.registerId q.contextId →
    LiveResidual tr.result q.carrierId q.registerId q.contextId

theorem T158_live_residual_persistence_under_noninterfering_dle
    (R0 R1 : RegistryState) (q : ResidualRef) (tr : ResidualTransition)
    (hLive : LiveResidual R0 q.carrierId q.registerId q.contextId)
    (hNonInterfering : NonInterferingDLE tr q)
    (hApply : Apply tr R0 = R1) :
    LiveResidual R1 q.carrierId q.registerId q.contextId := by
  rw [← hApply]
  exact hNonInterfering R0 hLive

inductive ResidualKind where
  | targetPresence
  | historical
  | memory
  | signal
  | causal
  | information
  | genericTrace
  deriving DecidableEq, Repr

structure TypedResidual where
  residualId : Id
  kind : ResidualKind
  deriving DecidableEq, Repr

def ResidualType (q : TypedResidual) : ResidualKind := q.kind

def AdmissibleTranslation (q1 q2 : TypedResidual) : Prop :=
  q1.residualId = q2.residualId

def Interchangeable (q1 q2 : TypedResidual) : Prop :=
  ResidualType q1 = ResidualType q2 ∨ AdmissibleTranslation q1 q2

theorem T159_residual_type_separation
    (q1 q2 : TypedResidual)
    (hTypes : ResidualType q1 ≠ ResidualType q2)
    (hNoTranslation : ¬ AdmissibleTranslation q1 q2) :
    ¬ Interchangeable q1 q2 := by
  intro hInterchangeable
  rcases hInterchangeable with hSameType | hTranslation
  · exact hTypes hSameType
  · exact hNoTranslation hTranslation

structure ClusterBModel where
  modelId : Id
  sharedFacts : List Id
  liveResidualIds : List Id
  deriving Repr

def AdmissibleModelPair (M1 M2 : ClusterBModel) (_sharedFragment : List Id) : Prop :=
  M1.modelId ≠ M2.modelId

def AgreeOn (M1 M2 : ClusterBModel) (sharedFragment : List Id) : Prop :=
  M1.sharedFacts = sharedFragment ∧ M2.sharedFacts = sharedFragment

def NonEliminableFrom (q : Id) (sharedFragment : List Id) : Prop :=
  ∃ M1 M2 : ClusterBModel,
    AdmissibleModelPair M1 M2 sharedFragment ∧
    AgreeOn M1 M2 sharedFragment ∧
    ((q ∈ M1.liveResidualIds) ≠ (q ∈ M2.liveResidualIds))

theorem T160_model_pair_noneliminability_witness
    (M1 M2 : ClusterBModel) (sharedFragment : List Id) (q : Id)
    (hPair : AdmissibleModelPair M1 M2 sharedFragment)
    (hAgree : AgreeOn M1 M2 sharedFragment)
    (hDifference : (q ∈ M1.liveResidualIds) ≠ (q ∈ M2.liveResidualIds)) :
    NonEliminableFrom q sharedFragment := by
  exact ⟨M1, M2, hPair, hAgree, hDifference⟩

def DeclaredResidual (q : Id) (residualRegisters : List Id) : Prop :=
  q ∈ residualRegisters

def MinimalObstructionWitness (q : Id) (claim : Prop) : Prop :=
  ¬ claim

theorem T161_minimal_single_residual_obstruction
    (registry : RegistryState) (carrier context q : Id)
    (residualRegisters : List Id)
    (hDeclared : DeclaredResidual q residualRegisters)
    (hLive : LiveResidual registry carrier q context) :
    MinimalObstructionWitness q
      (RawRelativeV0 registry carrier context residualRegisters) := by
  exact T134_raw_residual_obstruction
    registry carrier context q residualRegisters hDeclared hLive

def HistoricalToken (token : Token) : Prop :=
  token.partition = TokenPartition.historical ∨
  token.partition = TokenPartition.retired

def CurrentLiveGuardToken (token : Token) : Prop :=
  token.partition = TokenPartition.live

def FreshActivation (prior current : Token) : Prop :=
  HistoricalToken prior ∧ CurrentLiveGuardToken current

theorem T162_historical_live_token_nonconversion
    (prior current : Token)
    (hHistorical : HistoricalToken prior)
    (hNoFreshActivation : ¬ FreshActivation prior current) :
    ¬ CurrentLiveGuardToken current := by
  intro hCurrent
  exact hNoFreshActivation ⟨hHistorical, hCurrent⟩

end V0OSAP
