
import V0OSAP.Observer
import V0OSAP.Branches

namespace V0OSAP

structure ArchiveGuardExport where
  archiveId : Id
  observerId : Id
  registerId : Id
  contextId : Id
  exportsCurrentGuard : Bool
  deriving DecidableEq, Repr

def ArchiveNonGuardExport (record : ArchiveGuardExport) : Prop :=
  record.exportsCurrentGuard = false

theorem T139_archive_non_guard_export
    (record : ArchiveGuardExport)
    (h : ArchiveNonGuardExport record) :
    record.exportsCurrentGuard = false := h


structure IndependentWitnessCertificate where
  witnessId : Id
  observerId : Id
  policyCompliant : Bool
  nonCircular : Bool
  identityVerified : Bool
  evidenceVerified : Bool
  externalEvidenceIds : List Id
  independenceGroupIds : List Id
  deriving Repr

def IndependentWitnessAdmissible
    (certificate : IndependentWitnessCertificate) : Prop :=
  certificate.policyCompliant = true ∧
  certificate.nonCircular = true ∧
  certificate.identityVerified = true ∧
  certificate.evidenceVerified = true ∧
  certificate.externalEvidenceIds ≠ [] ∧
  certificate.independenceGroupIds ≠ []

def ExternalCertificateSupported
    (certificate : IndependentWitnessCertificate) : Prop :=
  certificate.externalEvidenceIds ≠ [] ∧
  certificate.independenceGroupIds ≠ []

theorem T140_independent_witness_conditional_sufficiency
    (certificate : IndependentWitnessCertificate)
    (h : IndependentWitnessAdmissible certificate) :
    ExternalCertificateSupported certificate := by
  exact ⟨h.2.2.2.2.1, h.2.2.2.2.2⟩


inductive ContainmentMode where
  | none
  | ordinary
  | typedMeta
  deriving DecidableEq, Repr

structure V0BranchContainment where
  containerId : Id
  branchId : Id
  mode : ContainmentMode
  deriving DecidableEq, Repr

def NoOrdinaryContainer (record : V0BranchContainment) : Prop :=
  record.mode ≠ ContainmentMode.ordinary

theorem T141_no_container
    (record : V0BranchContainment)
    (hOrdinary : record.mode = ContainmentMode.ordinary) :
    ¬ NoOrdinaryContainer record := by
  intro hNo
  exact hNo hOrdinary


inductive DistinctnessBasis where
  | labelOnly
  | nonIsomorphism
  | incompatibleProfile
  | observationalSeparation
  | registeredPolicy
  deriving DecidableEq, Repr

structure BranchDistinctnessCertificate where
  leftBranchId : Id
  rightBranchId : Id
  leftLabel : String
  rightLabel : String
  basis : DistinctnessBasis
  evidenceIds : List Id
  deriving Repr

def LabelIndependentDistinctness
    (certificate : BranchDistinctnessCertificate) : Prop :=
  certificate.basis ≠ DistinctnessBasis.labelOnly

theorem T142_branch_label_insufficiency
    (certificate : BranchDistinctnessCertificate)
    (hLabelOnly : certificate.basis = DistinctnessBasis.labelOnly) :
    ¬ LabelIndependentDistinctness certificate := by
  intro hDistinct
  exact hDistinct hLabelOnly


inductive CardinalityKind where
  | finiteEnumerated
  | countable
  | uncountable
  | properClass
  deriving DecidableEq, Repr

structure CardinalityCertificate where
  kind : CardinalityKind
  metaIndexId : Option Id
  evidenceIds : List Id
  deriving Repr

def NonFiniteKind (certificate : CardinalityCertificate) : Prop :=
  certificate.kind ≠ CardinalityKind.finiteEnumerated

def CardinalityLicensed (certificate : CardinalityCertificate) : Prop :=
  certificate.kind = CardinalityKind.finiteEnumerated ∨
  (certificate.kind ≠ CardinalityKind.finiteEnumerated ∧
    ∃ indexId, certificate.metaIndexId = some indexId ∧ certificate.evidenceIds ≠ [])

theorem T143_cardinality_licensing
    (certificate : CardinalityCertificate)
    (hNonFinite : NonFiniteKind certificate)
    (hLicensed : CardinalityLicensed certificate) :
    ∃ indexId, certificate.metaIndexId = some indexId ∧ certificate.evidenceIds ≠ [] := by
  rcases hLicensed with hFinite | hLicensedNonFinite
  · exact False.elim (hNonFinite hFinite)
  · exact hLicensedNonFinite.2


inductive DiagnosticStatus where
  | pass
  | outOfScope
  | indeterminate
  | deferred
  | reject
  deriving DecidableEq, Repr

def diagnosticStatusRank : DiagnosticStatus → Nat
  | DiagnosticStatus.pass => 0
  | DiagnosticStatus.outOfScope => 1
  | DiagnosticStatus.indeterminate => 2
  | DiagnosticStatus.deferred => 3
  | DiagnosticStatus.reject => 4

def choosePrimaryStatus
    (current candidate : DiagnosticStatus) : DiagnosticStatus :=
  if diagnosticStatusRank current ≤ diagnosticStatusRank candidate then candidate else current

def primaryStatus : List DiagnosticStatus → DiagnosticStatus
  | [] => DiagnosticStatus.pass
  | head :: tail => tail.foldl choosePrimaryStatus head

theorem T144_diagnostic_precedence_totality
    (statuses : List DiagnosticStatus) :
    Exists fun primary : DiagnosticStatus =>
      primary = primaryStatus statuses ∧
      ∀ other : DiagnosticStatus,
        other = primaryStatus statuses → other = primary := by
  refine ⟨primaryStatus statuses, rfl, ?_⟩
  intro other hOther
  exact hOther

end V0OSAP
