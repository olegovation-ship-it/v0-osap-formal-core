from __future__ import annotations

import hashlib
import json
from typing import Any

CANONICALIZATION_ID = "V0-OSAP-CJ-1"


def canonical_bytes(value: Any) -> bytes:
    """Return the unique FC-1 canonical UTF-8 JSON byte representation."""
    text = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )
    return (text + "\n").encode("utf-8")


def canonical_text(value: Any) -> str:
    return canonical_bytes(value).decode("utf-8")


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def parse_canonical_bytes(payload: bytes) -> Any:
    """Parse bytes only when they are already in V0-OSAP-CJ-1 form."""
    if payload.startswith(b"\xef\xbb\xbf"):
        raise ValueError("V0-OSAP-CJ-1 forbids a UTF-8 BOM.")
    value = json.loads(payload.decode("utf-8"))
    if canonical_bytes(value) != payload:
        raise ValueError("Input bytes are not canonical V0-OSAP-CJ-1 bytes.")
    return value


def canonical_round_trip(value: Any) -> Any:
    """Canonical serialize/parse round trip for a JSON-compatible value."""
    return parse_canonical_bytes(canonical_bytes(value))


def hash_envelope(
    value: Any,
    *,
    payload_schema_id: str,
    payload_schema_version: str,
) -> dict[str, Any]:
    payload = canonical_bytes(value)
    return {
        "algorithm": "sha256",
        "canonicalization": CANONICALIZATION_ID,
        "payload_schema_id": payload_schema_id,
        "payload_schema_version": payload_schema_version,
        "payload_hash": hashlib.sha256(payload).hexdigest(),
        "byte_length": len(payload),
    }
