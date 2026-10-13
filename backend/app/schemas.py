from typing import Any
from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    email: str
    password: str


class UserResponse(BaseModel):
    email: str
    full_name: str
    role: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class RunCreate(BaseModel):
    requirements: dict[str, Any] = Field(default_factory=dict)


class RunResponse(BaseModel):
    run_id: str
    status: str
    current_step: str | None = None
    scenario_count: int = 0
    script_count: int = 0
    error: str | None = None


class ScenarioResponse(BaseModel):
    id: str
    submodel: str
    type: str
    title: str
    description: str
    injected_fault: str | None = None
    expected_result: str


class ScriptResponse(BaseModel):
    id: str
    name: str
    path: str
    content: str
    execution_success: bool | None = None
    skipped: bool = False
    error: str | None = None
    duration_seconds: float | None = None
