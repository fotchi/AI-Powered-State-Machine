from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class RunRecord:
    id: str
    status: str = "pending"
    current_step: str = "queued"
    created_at: str = field(default_factory=utc_now)
    started_at: str | None = None
    completed_at: str | None = None
    requirements: dict[str, Any] = field(default_factory=dict)
    error: str | None = None
    logs: list[str] = field(default_factory=list)
    scenario_count: int = 0
    script_count: int = 0
