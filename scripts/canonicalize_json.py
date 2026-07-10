from __future__ import annotations

import json
import sys
from pathlib import Path

from v0_osap_fc1.canonical import canonical_text

if len(sys.argv) != 2:
    raise SystemExit("usage: canonicalize_json.py FILE")
path = Path(sys.argv[1])
value = json.loads(path.read_text(encoding="utf-8"))
sys.stdout.write(canonical_text(value))
