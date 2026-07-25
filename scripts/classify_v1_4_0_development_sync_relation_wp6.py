#!/usr/bin/env python3
from __future__ import annotations
import argparse, json
from dataclasses import asdict, dataclass

@dataclass(frozen=True)
class RelationDecision:
    main_ahead: int
    development_ahead: int
    decision: str
    action: str
    allowed: bool
    diagnostic: str

def classify(main_ahead: int, development_ahead: int) -> RelationDecision:
    if main_ahead < 0 or development_ahead < 0:
        return RelationDecision(main_ahead, development_ahead, "REJECT_INVALID_COUNTS", "NONE", False, "NEGATIVE_DIVERGENCE_COUNT")
    if main_ahead == 0 and development_ahead == 0:
        return RelationDecision(main_ahead, development_ahead, "ALREADY_SYNCHRONIZED", "NOOP", True, "NONE")
    if main_ahead > 0 and development_ahead == 0:
        return RelationDecision(main_ahead, development_ahead, "FAST_FORWARD_ALLOWED", "FAST_FORWARD", True, "NONE")
    if main_ahead == 0 and development_ahead > 0:
        return RelationDecision(main_ahead, development_ahead, "REJECT_DEVELOPMENT_AHEAD", "NONE", False, "DEVELOPMENT_NOT_CONTAINED_BY_MAIN")
    return RelationDecision(main_ahead, development_ahead, "REJECT_DIVERGED", "NONE", False, "BRANCHES_DIVERGED")

def main() -> int:
    p=argparse.ArgumentParser(); p.add_argument('--main-ahead',type=int,required=True); p.add_argument('--development-ahead',type=int,required=True); p.add_argument('--format',choices=('json','shell'),default='json'); a=p.parse_args()
    r=classify(a.main_ahead,a.development_ahead)
    if a.format=='shell':
        print(f"DECISION={r.decision}"); print(f"ACTION={r.action}"); print(f"ALLOWED={'true' if r.allowed else 'false'}"); print(f"DIAGNOSTIC={r.diagnostic}")
    else: print(json.dumps(asdict(r),sort_keys=True))
    return 0 if r.allowed else 1
if __name__=='__main__': raise SystemExit(main())
