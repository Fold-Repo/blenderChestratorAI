"""Public MVP-5 deterministic Blender tool API."""

from .builtin import register_builtin_tools
from .contracts import PermissionLevel, ToolExecutionContext
from .executor import ToolExecutor
from .registry import ToolRegistry
from .approval import execute_approved_transform, preview_transform_proposal


def create_tool_executor() -> ToolExecutor:
    registry = ToolRegistry()
    register_builtin_tools(registry)
    return ToolExecutor(registry)


__all__ = ("PermissionLevel", "ToolExecutionContext", "ToolExecutor", "ToolRegistry", "create_tool_executor", "execute_approved_transform", "preview_transform_proposal")
