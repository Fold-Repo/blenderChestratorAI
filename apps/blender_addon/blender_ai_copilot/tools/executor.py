"""Validated executor and audit result envelope for deterministic Blender tools."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from .contracts import PermissionLevel, ToolExecutionContext, ToolValidationError
from .registry import ToolRegistry


class ToolExecutor:
    def __init__(self, registry: ToolRegistry):
        self._registry = registry

    @property
    def registry(self) -> ToolRegistry:
        """Expose definitions for discovery without allowing registry replacement."""
        return self._registry

    def execute(
        self,
        name: str,
        arguments: Any,
        context: ToolExecutionContext,
    ) -> dict[str, Any]:
        tool = self._registry.get(name)
        if tool is None:
            return self._failure(name, "TOOL_NOT_FOUND", "Tool is not allow-listed.", context)

        audit = self._audit_base(tool.name, tool.version, tool.permission_level, context)
        try:
            self._validate_scope(context)
            if not isinstance(arguments, dict):
                raise ToolValidationError("INVALID_ARGUMENTS", "Tool arguments must be an object.")
            validated = tool.validator(arguments, context)
            result = tool.executor(validated, context)
            audit["outcome"] = "success"
            audit["target_count"] = int(result.get("count", 0))
            return {"ok": True, "result": result, "error": None, "audit": audit}
        except ToolValidationError as error:
            audit["outcome"] = "rejected"
            audit["error_code"] = error.code
            return {"ok": False, "result": None, "error": self._error(error.code, error.message), "audit": audit}
        except Exception:  # Blender API failures must not escape into the agent loop.
            audit["outcome"] = "failed"
            audit["error_code"] = "EXECUTION_FAILED"
            return {
                "ok": False,
                "result": None,
                "error": self._error("EXECUTION_FAILED", "Tool execution failed."),
                "audit": audit,
            }

    @staticmethod
    def _validate_scope(context: ToolExecutionContext) -> None:
        scene_name = str(getattr(context.scene, "name", ""))
        if context.expected_scene_name and context.expected_scene_name != scene_name:
            raise ToolValidationError("SCENE_SCOPE_MISMATCH", "The requested scene is not active.")

    @staticmethod
    def _error(code: str, message: str) -> dict[str, str]:
        return {"code": code, "message": message}

    def _failure(
        self, name: str, code: str, message: str, context: ToolExecutionContext
    ) -> dict[str, Any]:
        audit = self._audit_base(name, None, None, context)
        audit.update({"outcome": "rejected", "error_code": code})
        return {"ok": False, "result": None, "error": self._error(code, message), "audit": audit}

    @staticmethod
    def _audit_base(
        name: str,
        version: str | None,
        permission: PermissionLevel | None,
        context: ToolExecutionContext,
    ) -> dict[str, Any]:
        return {
            "tool_name": name,
            "tool_version": version,
            "permission_level": permission.value if permission else None,
            "project_id": context.project_id,
            "scene_name": str(getattr(context.scene, "name", "")),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
