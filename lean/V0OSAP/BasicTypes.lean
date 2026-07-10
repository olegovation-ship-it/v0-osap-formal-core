namespace V0OSAP

abbrev Id := String

inductive TokenPartition where
  | live
  | historical
  | retired
  | deferred
  deriving DecidableEq, Repr

structure Token where
  tokenId : Id
  carrierId : Id
  registerId : Id
  contextId : Id
  partition : TokenPartition
  introducedIn : Id
  sourceEvidenceId : Id
  deriving DecidableEq, Repr

inductive PrerequisiteMode where
  | allOf
  | oneOf
  deriving DecidableEq, Repr

structure PrerequisiteFamily where
  familyId : Id
  targetRegisterId : Id
  mode : PrerequisiteMode
  prerequisiteRegisterIds : List Id
  enabled : Bool
  deriving DecidableEq, Repr

structure Claim where
  claimId : Id
  kind : Id
  carrierId : Option Id := none
  registerId : Option Id := none
  contextId : Option Id := none
  sourceClaimId : Option Id := none
  deriving DecidableEq, Repr

end V0OSAP
