import V0OSAP.BasicTypes

namespace V0OSAP

structure RegistryState where
  stateId : Id
  tokens : List Token
  prerequisiteFamilies : List PrerequisiteFamily
  claims : List Claim
  deriving Repr


def Token.matches (token : Token) (carrier register context : Id) : Prop :=
  token.carrierId = carrier ∧ token.registerId = register ∧ token.contextId = context

end V0OSAP
