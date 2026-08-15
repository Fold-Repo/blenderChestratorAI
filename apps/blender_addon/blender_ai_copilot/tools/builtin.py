"""MVP-5 allow-listed Blender tools and their strict local validators."""

from __future__ import annotations

from typing import Any

from ..context.collector import _stable_object_identifier, collect_context, collect_object_context
from .contracts import PermissionLevel, ToolDefinition, ToolExecutionContext, ToolValidationError
from .registry import ToolRegistry

_MAX_TARGETS = 100
_MAX_TRANSFORM_TARGETS = 50
_MAX_LOCATION_DELTA = 1000.0
_MAX_ROTATION_DELTA = 6.283185307179586
_MIN_SCALE = 0.01
_MAX_SCALE = 100.0


def _no_arguments(arguments: dict[str, Any], _: ToolExecutionContext) -> dict[str, Any]:
    if arguments:
        raise ToolValidationError("INVALID_ARGUMENTS", "This tool does not accept arguments.")
    return {}


def _scene_objects(context: ToolExecutionContext) -> list[Any]:
    return list(getattr(context.scene, "objects", []))


def _object_index(context: ToolExecutionContext) -> dict[str, Any]:
    index: dict[str, Any] = {}
    for obj in _scene_objects(context):
        object_id = _stable_object_identifier(obj)
        if object_id in index:
            raise ToolValidationError("AMBIGUOUS_OBJECT_ID", "Scene contains duplicate object IDs.")
        index[object_id] = obj
    return index


def _validate_find(arguments: dict[str, Any], _: ToolExecutionContext) -> dict[str, Any]:
    allowed = {"exact_name", "contains", "type", "collection"}
    unknown = set(arguments) - allowed
    if unknown or not arguments:
        raise ToolValidationError("INVALID_ARGUMENTS", "Provide one or more supported search filters.")
    cleaned: dict[str, str] = {}
    for key, value in arguments.items():
        if not isinstance(value, str) or not value.strip() or len(value) > 256:
            raise ToolValidationError("INVALID_ARGUMENTS", f"{key} must be a non-empty string.")
        cleaned[key] = value.strip()
    return cleaned


def _validate_select(arguments: dict[str, Any], context: ToolExecutionContext) -> dict[str, Any]:
    if set(arguments) - {"object_ids", "replace_selection"} or "object_ids" not in arguments:
        raise ToolValidationError("INVALID_ARGUMENTS", "object_ids is required.")
    object_ids = arguments["object_ids"]
    if not isinstance(object_ids, list) or not object_ids or len(object_ids) > _MAX_TARGETS:
        raise ToolValidationError("INVALID_ARGUMENTS", "object_ids must contain 1 to 100 IDs.")
    if any(not isinstance(object_id, str) or not object_id for object_id in object_ids):
        raise ToolValidationError("INVALID_ARGUMENTS", "Each object ID must be a non-empty string.")
    if len(set(object_ids)) != len(object_ids):
        raise ToolValidationError("INVALID_ARGUMENTS", "object_ids must not contain duplicates.")
    replace_selection = arguments.get("replace_selection", True)
    if not isinstance(replace_selection, bool):
        raise ToolValidationError("INVALID_ARGUMENTS", "replace_selection must be a boolean.")
    index = _object_index(context)
    unknown_ids = [object_id for object_id in object_ids if object_id not in index]
    if unknown_ids:
        raise ToolValidationError("UNKNOWN_OBJECT_ID", "One or more object IDs are not in the active scene.")
    return {"object_ids": object_ids, "replace_selection": replace_selection}


def _validate_transform_placeholder(
    arguments: dict[str, Any], context: ToolExecutionContext
) -> dict[str, Any]:
    allowed = {
        "object_ids",
        "location_delta",
        "rotation_delta",
        "scale_multiplier",
    }
    if set(arguments) - allowed or "object_ids" not in arguments:
        raise ToolValidationError("INVALID_ARGUMENTS", "object_ids is required.")

    target_arguments = _validate_select({"object_ids": arguments["object_ids"]}, context)
    if len(target_arguments["object_ids"]) > _MAX_TRANSFORM_TARGETS:
        raise ToolValidationError(
            "INVALID_ARGUMENTS",
            f"object_ids must contain no more than {_MAX_TRANSFORM_TARGETS} IDs.",
        )
    validated: dict[str, Any] = {"object_ids": target_arguments["object_ids"]}
    bounds = {
        "location_delta": _MAX_LOCATION_DELTA,
        "rotation_delta": _MAX_ROTATION_DELTA,
    }
    for key in ("location_delta", "rotation_delta"):
        if key not in arguments:
            continue
        value = arguments[key]
        if (
            not isinstance(value, list)
            or len(value) != 3
            or any(
                isinstance(item, bool)
                or not isinstance(item, (int, float))
                or abs(item) > bounds[key]
                for item in value
            )
        ):
            raise ToolValidationError(
                "INVALID_ARGUMENTS", f"{key} must contain three bounded numbers."
            )
        validated[key] = [float(item) for item in value]

    if "scale_multiplier" in arguments:
        value = arguments["scale_multiplier"]
        if (
            not isinstance(value, list)
            or len(value) != 3
            or any(
                isinstance(item, bool)
                or not isinstance(item, (int, float))
                or item < _MIN_SCALE
                or item > _MAX_SCALE
                for item in value
            )
        ):
            raise ToolValidationError(
                "INVALID_ARGUMENTS",
                "scale_multiplier must contain three values between 0.01 and 100.",
            )
        validated["scale_multiplier"] = [float(item) for item in value]

    if (
        validated.get("location_delta", [0.0, 0.0, 0.0]) == [0.0, 0.0, 0.0]
        and validated.get("rotation_delta", [0.0, 0.0, 0.0]) == [0.0, 0.0, 0.0]
        and validated.get("scale_multiplier", [1.0, 1.0, 1.0]) == [1.0, 1.0, 1.0]
    ):
        raise ToolValidationError(
            "INVALID_ARGUMENTS", "A proposal must change at least one transform."
        )
    if not context.approved_proposal_id:
        raise ToolValidationError(
            "APPROVAL_REQUIRED", "Transform execution requires an approved proposal."
        )
    return validated


def _execute_scene_summary(_: dict[str, Any], context: ToolExecutionContext) -> dict[str, Any]:
    return {"scene": collect_context(context.scene, [])["scene"], "count": 0}


def _execute_selected(_: dict[str, Any], context: ToolExecutionContext) -> dict[str, Any]:
    objects = [collect_object_context(obj) for obj in context.selected_objects]
    return {"objects": objects, "count": len(objects)}


def _execute_find(filters: dict[str, str], context: ToolExecutionContext) -> dict[str, Any]:
    matched = []
    for obj in _scene_objects(context):
        name = str(getattr(obj, "name", ""))
        obj_type = str(getattr(obj, "type", ""))
        collections = [str(getattr(item, "name", "")) for item in getattr(obj, "users_collection", [])]
        if "exact_name" in filters and name != filters["exact_name"]:
            continue
        if "contains" in filters and filters["contains"].casefold() not in name.casefold():
            continue
        if "type" in filters and obj_type != filters["type"]:
            continue
        if "collection" in filters and filters["collection"] not in collections:
            continue
        matched.append(collect_object_context(obj))
    return {"objects": matched, "count": len(matched), "filters": filters}


def _execute_select(arguments: dict[str, Any], context: ToolExecutionContext) -> dict[str, Any]:
    index = _object_index(context)
    selected = [index[object_id] for object_id in arguments["object_ids"]]
    if arguments["replace_selection"]:
        for obj in _scene_objects(context):
            obj.select_set(False)
    for obj in selected:
        obj.select_set(True)
    return {"object_ids": arguments["object_ids"], "count": len(selected), "replace_selection": arguments["replace_selection"]}


def _execute_transform(
    arguments: dict[str, Any], context: ToolExecutionContext
) -> dict[str, Any]:
    index = _object_index(context)
    changed = []
    location_delta = arguments.get("location_delta", [0.0, 0.0, 0.0])
    rotation_delta = arguments.get("rotation_delta", [0.0, 0.0, 0.0])
    scale_multiplier = arguments.get("scale_multiplier", [1.0, 1.0, 1.0])
    for object_id in arguments["object_ids"]:
        obj = index[object_id]
        before = collect_object_context(obj)
        obj.location = [before["location"][i] + location_delta[i] for i in range(3)]
        obj.rotation_euler = [
            before["rotation"][i] + rotation_delta[i] for i in range(3)
        ]
        obj.scale = [before["scale"][i] * scale_multiplier[i] for i in range(3)]
        after = collect_object_context(obj)
        changed.append({"id": object_id, "before": before, "after": after})
    return {
        "proposal_id": context.approved_proposal_id,
        "objects": changed,
        "count": len(changed),
    }


def _schema(properties: dict[str, Any], required: list[str] | None = None) -> dict[str, Any]:
    return {"type": "object", "additionalProperties": False, "properties": properties, "required": required or []}


def register_builtin_tools(registry: ToolRegistry) -> None:
    common_errors = ("INVALID_ARGUMENTS", "SCENE_SCOPE_MISMATCH", "EXECUTION_FAILED")
    registry.register(ToolDefinition("get_scene_summary", "1", "Return active-scene metadata.", _schema({}), _schema({"scene": {"type": "object"}, "count": {"type": "integer"}}), PermissionLevel.READ_ONLY, _no_arguments, _execute_scene_summary, common_errors, 5.0, ("project_id", "scene_name", "timestamp")))
    registry.register(ToolDefinition("get_selected_objects", "1", "Return selected objects and transforms.", _schema({}), _schema({"objects": {"type": "array"}, "count": {"type": "integer"}}), PermissionLevel.READ_ONLY, _no_arguments, _execute_selected, common_errors, 5.0, ("project_id", "scene_name", "timestamp")))
    registry.register(ToolDefinition("find_objects", "1", "Find active-scene objects using deterministic filters.", _schema({"exact_name": {"type": "string"}, "contains": {"type": "string"}, "type": {"type": "string"}, "collection": {"type": "string"}}), _schema({"objects": {"type": "array"}, "count": {"type": "integer"}, "filters": {"type": "object"}}), PermissionLevel.READ_ONLY, _validate_find, _execute_find, common_errors, 5.0, ("project_id", "scene_name", "timestamp", "target_count")))
    registry.register(ToolDefinition("select_objects", "1", "Select known objects in the active scene.", _schema({"object_ids": {"type": "array", "items": {"type": "string"}}, "replace_selection": {"type": "boolean"}}, ["object_ids"]), _schema({"object_ids": {"type": "array"}, "count": {"type": "integer"}}), PermissionLevel.SAFE_WRITE, _validate_select, _execute_select, common_errors + ("UNKNOWN_OBJECT_ID",), 5.0, ("project_id", "scene_name", "timestamp", "target_count")))
    registry.register(ToolDefinition("modify_object_transform", "1", "Apply an approved bounded object transform.", _schema({"object_ids": {"type": "array"}, "location_delta": {"type": "array"}, "rotation_delta": {"type": "array"}, "scale_multiplier": {"type": "array"}}, ["object_ids"]), _schema({"objects": {"type": "array"}, "count": {"type": "integer"}}), PermissionLevel.APPROVAL_REQUIRED, _validate_transform_placeholder, _execute_transform, ("INVALID_ARGUMENTS", "UNKNOWN_OBJECT_ID", "APPROVAL_REQUIRED"), 5.0, ("project_id", "scene_name", "timestamp", "target_count")))
