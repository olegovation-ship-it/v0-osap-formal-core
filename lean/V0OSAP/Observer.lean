import V0OSAP.BasicTypes

namespace V0OSAP

structure ObserverSupport where
  observerId : Id
  internalSupportIds : List Id
  externalEvidenceIds : List Id
  independenceGroupIds : List Id
  deriving Repr


def TerminalSelfCertificate (support : ObserverSupport) : Prop :=
  support.internalSupportIds = [] ∧ support.externalEvidenceIds = []


def AdmissibleObserverCertificate (support : ObserverSupport) : Prop :=
  support.externalEvidenceIds ≠ [] ∧ support.independenceGroupIds ≠ []


theorem terminal_self_certificate_exposes_empty_support
    (support : ObserverSupport) (h : TerminalSelfCertificate support) :
    support.internalSupportIds = [] ∧ support.externalEvidenceIds = [] := h


theorem admissible_observer_certificate_has_external_independent_support
    (support : ObserverSupport) (h : AdmissibleObserverCertificate support) :
    support.externalEvidenceIds ≠ [] ∧ support.independenceGroupIds ≠ [] := h

end V0OSAP
