"""Deterministic Blender scene context collector for MVP-4."""

from __future__ import annotations

from typing import Any


def _safe_name(value: Any, default: str = "") -> str:
    return str(value) if value is not None else default


def _vec3(values: Any) -> list[float]:
    if values is None:
        return [0.0, 0.0, 0.0]

    output = []
    for index in range(3):
        try:
            output.append(float(values[index]))
        except (TypeError, ValueError, IndexError):
            output.append(0.0)
    return output


def _collection_names(obj: Any) -> list[str]:
    collections = getattr(obj, "users_collection", [])
    return [str(getattr(collection, "name", "")) for collection in collections if collection]


def _material_names(obj: Any) -> list[str]:
    slots = getattr(obj, "material_slots", [])
    names = []
    for slot in slots:
        material = getattr(slot, "material", None)
        if material is not None:
            names.append(str(getattr(material, "name", "")))
    return names


def _modifier_summary(obj: Any) -> list[dict[str, str]]:
    modifiers = getattr(obj, "modifiers", [])
    return [
        {
            "name": str(getattr(modifier, "name", "")),
            "type": str(getattr(modifier, "type", "")),
        }
        for modifier in modifiers
    ]


def _mesh_stats(obj: Any) -> dict[str, int] | None:
    if str(getattr(obj, "type", "")) != "MESH":
        return None

    data = getattr(obj, "data", None)
    if data is None:
        return {"vertices": 0, "edges": 0, "faces": 0}

    return {
        "vertices": len(getattr(data, "vertices", [])),
        "edges": len(getattr(data, "edges", [])),
        "faces": len(getattr(data, "polygons", [])),
    }


def _stable_object_identifier(obj: Any) -> str:
    if hasattr(obj, "get"):
        custom_id = obj.get("blender_ai_copilot_id")
        if custom_id:
            return str(custom_id)

    name = _safe_name(getattr(obj, "name", "unnamed"), "unnamed")
    obj_type = _safe_name(getattr(obj, "type", "UNKNOWN"), "UNKNOWN")
    return f"obj:{obj_type}:{name}"


def collect_object_context(obj: Any) -> dict[str, Any]:
    return {
        "id": _stable_object_identifier(obj),
        "name": _safe_name(getattr(obj, "name", "")),
        "type": _safe_name(getattr(obj, "type", "")),
        "location": _vec3(getattr(obj, "location", None)),
        "rotation": _vec3(getattr(obj, "rotation_euler", None)),
        "scale": _vec3(getattr(obj, "scale", None)),
        "collections": _collection_names(obj),
        "materials": _material_names(obj),
        "modifiers": _modifier_summary(obj),
        "mesh_stats": _mesh_stats(obj),
    }


def _scene_summary(scene: Any, active_scene_name: str) -> dict[str, Any]:
    objects = list(getattr(scene, "objects", []))
    cameras = [obj for obj in objects if str(getattr(obj, "type", "")) == "CAMERA"]
    lights = [obj for obj in objects if str(getattr(obj, "type", "")) == "LIGHT"]

    return {
        "scene_name": _safe_name(getattr(scene, "name", "")),
        "active_scene": active_scene_name,
        "frame": int(getattr(scene, "frame_current", 0) or 0),
        "render_engine": _safe_name(
            getattr(getattr(scene, "render", None), "engine", ""),
            "",
        ),
        "object_count": len(objects),
        "camera_count": len(cameras),
        "light_count": len(lights),
        "collections": [
            str(getattr(collection, "name", ""))
            for collection in getattr(scene, "collection", None).children
        ]
        if getattr(scene, "collection", None) is not None
        else [],
    }


def _selection_summary(selected_objects: list[Any]) -> dict[str, Any]:
    detailed = [collect_object_context(obj) for obj in selected_objects]
    return {
        "selected_object_ids": [item["id"] for item in detailed],
        "selected_object_names": [item["name"] for item in detailed],
        "selected_object_types": [item["type"] for item in detailed],
        "selected_transforms": [
            {
                "id": item["id"],
                "location": item["location"],
                "rotation": item["rotation"],
                "scale": item["scale"],
            }
            for item in detailed
        ],
    }


def collect_context(scene: Any, selected_objects: list[Any] | None = None) -> dict[str, Any]:
    selected = selected_objects if selected_objects is not None else []

    active_scene_name = _safe_name(getattr(scene, "name", ""))
    scene_data = _scene_summary(scene, active_scene_name)
    selection_data = _selection_summary(list(selected))

    relevant_objects = list(selected)
    if not relevant_objects:
        relevant_objects = list(getattr(scene, "objects", []))[:25]

    return {
        "scene": scene_data,
        "objects": [collect_object_context(obj) for obj in relevant_objects],
        "selection": selection_data,
    }
