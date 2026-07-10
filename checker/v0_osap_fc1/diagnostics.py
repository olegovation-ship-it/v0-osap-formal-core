from __future__ import annotations

from dataclasses import asdict, dataclass, field

STATUS_RANK = {
    "PASS": 0,
    "OUT-OF-SCOPE": 1,
    "INDETERMINATE": 2,
    "DEFERRED": 3,
    "REJECT": 4,
}


@dataclass(frozen=True)
class Diagnostic:
    code: str
    status: str
    priority: int
    message: str
    instance_path: str = ""
    related_ids: tuple[str, ...] = field(default_factory=tuple)
    evidence_ids: tuple[str, ...] = field(default_factory=tuple)

    def to_dict(self) -> dict[str, object]:
        data = asdict(self)
        data["related_ids"] = list(self.related_ids)
        data["evidence_ids"] = list(self.evidence_ids)
        return data


def sort_diagnostics(items: list[Diagnostic]) -> list[Diagnostic]:
    return sorted(items, key=lambda d: (-d.priority, d.code, d.instance_path, d.related_ids))


def aggregate_status(items: list[Diagnostic]) -> str:
    if not items:
        return "PASS"
    return max((d.status for d in items), key=lambda s: STATUS_RANK[s])
