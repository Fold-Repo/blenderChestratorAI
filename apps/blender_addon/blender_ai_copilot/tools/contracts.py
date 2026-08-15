"""Versioned, deterministic contracts for Blender scene tools."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable


class PermissionLevel(str, Enum):
    READ_ONLY = "READ_ONLY"
    SAFE_WRITE = "SAFE_WRITE"
    APPROVAL_REQUIRED = "APPROVAL_REQUIRED"


class ToolValidationError(ValueError):
    """A tool argument or target failed local policy validation."""

    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code
        self.message = message


Validator = Callable[[dict[str, Any], "ToolExecutionContext"], dict[str, Any]]
Executor = Callable[[dict[str, Any], "ToolExecutionContext"], dict[str, Any]]


@dataclass(frozen=True)
class ToolExecutionContext:
    """Trusted execution context supplied by the add-on, never by the model."""

    scene: Any
    selected_objects: list[Any]
    project_id: str | None = None
    expected_scene_name: str | None = None
    approved_proposal_id: str | None = None


@dataclass(frozen=True)
class ToolDefinition:
    name: str
    version: str
    description: str
    input_schema: dict[str, Any]
    result_schema: dict[str, Any]
    permission_level: PermissionLevel
    validator: Validator
    executor: Executor
    error_codes: tuple[str, ...]
    timeout_seconds: float
    audit_fields: tuple[str, ...]
