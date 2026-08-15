"""Preview and approved execution helpers for MVP-8 transform proposals."""

from __future__ import annotations

from dataclasses import replace
from typing import Any

from .builtin import (
    _object_index,
    _validate_transform_placeholder,
    register_builtin_tools,
)
from .contracts import ToolExecutionContext, ToolValidationError
from .executor import ToolExecutor
from .registry import ToolRegistry


def _arguments_from_proposal(proposal: dict[str, Any]) -> dict[str, Any]:
    arguments = proposal.get("execution_arguments")
    if not isinstance(arguments, dict):
        raise ToolValidationError("INVALID_PROPOSAL", "Proposal has no execution arguments.")
    return arguments


def preview_transform_proposal(
    proposal: dict[str, Any], context: ToolExecutionContext
) -> dict[str, Any]:
    """Validate a proposal against the current scene and calculate its outcome."""
    arguments = _arguments_from_proposal(proposal)
    preview_context = replace(context, approved_proposal_id="preview-only")
    validated = _validate_transform_placeholder(arguments, preview_context)
    index = _object_index(context)
    location_delta = validated.get("location_delta", [0.0, 0.0, 0.0])
    rotation_delta = validated.get("rotation_delta", [0.0, 0.0, 0.0])
    scale_multiplier = validated.get("scale_multiplier", [1.0, 1.0, 1.0])
    targets = []
    for object_id in validated["object_ids"]:
        obj = index[object_id]
        before = {
            "location": [float(obj.location[i]) for i in range(3)],
            "rotation": [float(obj.rotation_euler[i]) for i in range(3)],
            "scale": [float(obj.scale[i]) for i in range(3)],
        }
        targets.append(
            {
                "id": object_id,
                "before": before,
                "after": {
                    "location": [before["location"][i] + location_delta[i] for i in range(3)],
                    "rotation": [before["rotation"][i] + rotation_delta[i] for i in range(3)],
                    "scale": [before["scale"][i] * scale_multiplier[i] for i in range(3)],
                },
            }
        )
    return {"proposal_id": proposal.get("proposal_id", ""), "targets": targets, "count": len(targets)}


def execute_approved_transform(
    proposal: dict[str, Any], context: ToolExecutionContext
) -> dict[str, Any]:
    proposal_id = proposal.get("proposal_id")
    if not isinstance(proposal_id, str) or not proposal_id:
        raise ToolValidationError("INVALID_PROPOSAL", "Proposal ID is required for execution.")
    approved_context = replace(context, approved_proposal_id=proposal_id)
    registry = ToolRegistry()
    register_builtin_tools(registry)
    return ToolExecutor(registry).execute(
        "modify_object_transform", _arguments_from_proposal(proposal), approved_context
    )
