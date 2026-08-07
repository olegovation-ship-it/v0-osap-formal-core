#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
VERIFIER = ROOT / "release/v1.4.0/tools/verify_wp6_hosted_ci_predecessor_consumer_closure_repair.py"
CONSUMER = 'wp5-canonical-allowlist'


def main() -> int:
    if not VERIFIER.is_file():
        raise SystemExit("predecessor-consumer closure verifier is missing")
    spec = importlib.util.spec_from_file_location("wp6_predecessor_consumer_closure", VERIFIER)
    if spec is None or spec.loader is None:
        raise SystemExit("unable to load predecessor-consumer closure verifier")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return int(module.replay_consumer(CONSUMER, sys.argv[1:]))


if __name__ == "__main__":
    raise SystemExit(main())
