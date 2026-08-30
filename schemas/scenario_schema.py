"""
Strict interface contract shared by every module agent — WITHOUT pydantic
(project preference). Uses plain dataclasses + a manual validation
function instead.
"""
from dataclasses import dataclass, asdict
from enum import Enum
from typing import Optional


class ScenarioType(str, Enum):
    POSITIVE = "Positive"
    NEGATIVE = "Negative"


class ScenarioValidationError(Exception):
    """Raised when a raw dict does not match the Scenario contract."""


@dataclass
class Scenario:
    id: str
    submodel: str
    type: ScenarioType
    title: str
    description: str
    expected_result: str
    injected_fault: Optional[str] = None

    def to_dict(self) -> dict:
        d = asdict(self)
        d["type"] = self.type.value  # Enum -> plain string for JSON output
        return d


REQUIRED_FIELDS = ["id", "submodel", "type", "title", "description", "expected_result"]


def validate_scenario(data: dict) -> Scenario:
    """Validates a raw dict (typically parsed from LLM JSON output) and
    returns a Scenario, or raises ScenarioValidationError with a clear
    message about what's wrong.
    """
    if not isinstance(data, dict):
        raise ScenarioValidationError(f"Expected a dict, got {type(data).__name__}")

    missing = [f for f in REQUIRED_FIELDS if f not in data]
    if missing:
        raise ScenarioValidationError(f"Missing required field(s): {missing}")

    for field in REQUIRED_FIELDS:
        if not isinstance(data[field], str):
            raise ScenarioValidationError(
                f"Field '{field}' must be a string, got {type(data[field]).__name__}"
            )

    try:
        scenario_type = ScenarioType(data["type"])
    except ValueError:
        raise ScenarioValidationError(
            f"Field 'type' must be one of {[t.value for t in ScenarioType]}, got '{data['type']}'"
        )

    injected_fault = data.get("injected_fault")
    if injected_fault is not None and not isinstance(injected_fault, str):
        raise ScenarioValidationError("Field 'injected_fault' must be a string or null")

    # No unexpected extra fields — mirrors pydantic's extra="forbid"
    allowed = set(REQUIRED_FIELDS) | {"injected_fault"}
    extra = set(data.keys()) - allowed
    if extra:
        raise ScenarioValidationError(f"Unexpected field(s): {extra}")

    return Scenario(
        id=data["id"],
        submodel=data["submodel"],
        type=scenario_type,
        title=data["title"],
        description=data["description"],
        expected_result=data["expected_result"],
        injected_fault=injected_fault,
    )