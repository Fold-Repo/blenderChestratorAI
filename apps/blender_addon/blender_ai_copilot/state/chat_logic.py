"""Local mock chat state and transitions for MVP-2."""

from __future__ import annotations

import json
from copy import deepcopy
from datetime import datetime, timezone
from uuid import uuid4

UI_STATES = [
    "idle",
    "thinking",
    "tool_running",
    "proposal",
    "awaiting_approval",
    "executing",
    "completed",
    "error",
    "cancelled",
]


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def new_message(role: str, content: str, status: str = "done") -> dict:
    return {
        "id": str(uuid4()),
        "role": role,
        "content": content,
        "timestamp": now_iso(),
        "status": status,
    }


def default_session() -> dict:
    return {
        "ui_state": "idle",
        "messages": [],
        "tool_activity": {
            "status": "idle",
            "label": "No active tools",
        },
        "proposal": None,
        "last_error": "",
        "last_user_message": "",
        "can_retry": False,
        "undo_available": False,
        "last_action": None,
    }


def loads_session(raw: str) -> dict:
    if not raw:
        return default_session()

    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return default_session()

    base = default_session()
    base.update({k: data.get(k, v) for k, v in base.items()})

    if base["ui_state"] not in UI_STATES:
        base["ui_state"] = "idle"

    if not isinstance(base["messages"], list):
        base["messages"] = []

    if not isinstance(base["tool_activity"], dict):
        base["tool_activity"] = default_session()["tool_activity"]

    return base


def dumps_session(session: dict) -> str:
    return json.dumps(session)


def _append(session: dict, role: str, content: str, status: str = "done") -> None:
    session["messages"].append(new_message(role, content, status=status))


def begin_backend_turn(session: dict, text: str) -> dict:
    next_state = deepcopy(session)
    content = text.strip()
    if not content:
        return next_state

    next_state["last_user_message"] = content
    next_state["ui_state"] = "thinking"
    next_state["last_error"] = ""
    next_state["can_retry"] = False

    _append(next_state, "user", content)
    _append(next_state, "tool_started", "Submitting message to backend")
    next_state["tool_activity"] = {
        "status": "running",
        "label": "Waiting for backend response",
    }
    return next_state


def complete_backend_turn(
    session: dict,
    assistant_message: str,
    tool_calls: list[dict] | None = None,
) -> dict:
    next_state = deepcopy(session)
    _append(next_state, "assistant", assistant_message)
    tool_names = [
        str(call.get("name", "tool"))
        for call in (tool_calls or [])
        if isinstance(call, dict)
    ]
    completed_label = (
        f"Completed: {', '.join(tool_names)}"
        if tool_names
        else "Backend response received"
    )
    _append(next_state, "tool_completed", completed_label)
    next_state["ui_state"] = "completed"
    next_state["can_retry"] = False
    next_state["tool_activity"] = {
        "status": "completed",
        "label": completed_label,
    }
    return next_state


def await_agent_proposal(
    session: dict,
    assistant_message: str,
    proposal: dict,
    tool_calls: list[dict] | None = None,
) -> dict:
    next_state = deepcopy(session)
    next_state["proposal"] = {
        "source": "agent",
        "proposal_id": proposal.get("id", ""),
        "change": "Modify object transform",
        "targets": [item.get("name", item.get("id", "object")) for item in proposal.get("targets", [])],
        "parameters": (
            f"location={proposal.get('locationDelta', [0, 0, 0])}; "
            f"rotation={proposal.get('rotationDelta', [0, 0, 0])}; "
            f"scale={proposal.get('scaleMultiplier', [1, 1, 1])}"
        ),
        "risk": "approval required",
        "scene_area": proposal.get("sceneName", "Active scene"),
        "execution_arguments": {
            "object_ids": [item.get("id", "") for item in proposal.get("targets", [])],
            "location_delta": proposal.get("locationDelta", [0, 0, 0]),
            "rotation_delta": proposal.get("rotationDelta", [0, 0, 0]),
            "scale_multiplier": proposal.get("scaleMultiplier", [1, 1, 1]),
        },
    }
    _append(next_state, "assistant", assistant_message)
    _append(next_state, "action_proposal", "Transform proposal prepared")
    _append(next_state, "approval_request", "Approval is required before execution")
    next_state["ui_state"] = "awaiting_approval"
    next_state["can_retry"] = False
    next_state["tool_activity"] = {
        "status": "awaiting_approval",
        "label": "Transform proposal requires approval",
    }
    return next_state


def preview_agent_proposal(session: dict, preview: dict) -> dict:
    next_state = deepcopy(session)
    if not next_state.get("proposal") or next_state["proposal"].get("source") != "agent":
        return next_state
    next_state["proposal"]["preview"] = preview
    next_state["ui_state"] = "proposal"
    _append(next_state, "execution_result", "Preview generated; no scene changes made.")
    next_state["tool_activity"] = {"status": "previewed", "label": "Proposal preview ready"}
    return next_state


def complete_agent_execution(session: dict, result: dict) -> dict:
    next_state = deepcopy(session)
    next_state["proposal"] = None
    next_state["undo_available"] = True
    next_state["last_action"] = result
    next_state["ui_state"] = "completed"
    _append(next_state, "execution_result", "Approved transform applied.")
    _append(next_state, "tool_completed", "Transform execution completed")
    next_state["tool_activity"] = {"status": "completed", "label": "Transform applied; Undo is available"}
    return next_state


def record_undo(session: dict) -> dict:
    next_state = deepcopy(session)
    if not next_state.get("undo_available"):
        return next_state
    next_state["undo_available"] = False
    next_state["last_action"] = None
    next_state["ui_state"] = "completed"
    _append(next_state, "execution_result", "Last Copilot action undone.")
    next_state["tool_activity"] = {"status": "completed", "label": "Last action undone"}
    return next_state


def fail_backend_turn(session: dict, message: str) -> dict:
    next_state = deepcopy(session)
    next_state["ui_state"] = "error"
    next_state["last_error"] = message
    next_state["can_retry"] = True
    _append(next_state, "error", message, status="failed")
    next_state["tool_activity"] = {
        "status": "error",
        "label": "Backend request failed",
    }
    return next_state


def send_user_message(session: dict, text: str) -> dict:
    next_state = deepcopy(session)
    content = text.strip()
    if not content:
        return next_state

    next_state["last_user_message"] = content
    next_state["ui_state"] = "thinking"
    next_state["last_error"] = ""
    next_state["can_retry"] = False

    _append(next_state, "user", content)

    if content.lower() in {"/error", "error"}:
        next_state["ui_state"] = "error"
        next_state["can_retry"] = True
        next_state["last_error"] = "Mock response failed. Use Retry to continue."
        _append(next_state, "error", next_state["last_error"], status="failed")
        return next_state

    next_state["ui_state"] = "tool_running"
    next_state["tool_activity"] = {
        "status": "running",
        "label": "Preparing mock assistant response",
    }
    _append(next_state, "tool_started", "Mock tool started")

    next_state["tool_activity"] = {
        "status": "completed",
        "label": "Mock tool completed",
    }
    _append(next_state, "tool_completed", "Mock tool completed")

    if content.lower() == "hello":
        assistant = "Blender AI Copilot is ready."
    else:
        assistant = (
            "Mock response: I received your message and updated local conversation state."
        )

    _append(next_state, "assistant", assistant)
    next_state["ui_state"] = "completed"
    return next_state


def retry_last(session: dict) -> dict:
    next_state = deepcopy(session)

    if not next_state.get("can_retry"):
        return next_state

    next_state["ui_state"] = "thinking"
    next_state["last_error"] = ""
    _append(next_state, "warning", "Retry requested")

    next_state["tool_activity"] = {
        "status": "completed",
        "label": "Retry completed",
    }
    _append(next_state, "assistant", "Retry succeeded. Blender AI Copilot is ready.")

    next_state["ui_state"] = "completed"
    next_state["can_retry"] = False
    return next_state


def clear_conversation(_session: dict) -> dict:
    return default_session()


def cancel_current(session: dict) -> dict:
    next_state = deepcopy(session)
    next_state["ui_state"] = "cancelled"
    next_state["tool_activity"] = {
        "status": "cancelled",
        "label": "Current operation cancelled",
    }
    _append(next_state, "warning", "Operation cancelled by user.")
    return next_state


def seed_mock_proposal(session: dict) -> dict:
    next_state = deepcopy(session)
    next_state["proposal"] = {
        "change": "Move selected objects 2m left",
        "targets": ["Tree_A", "Tree_B"],
        "parameters": "x_offset=-2.0",
        "risk": "medium",
        "scene_area": "Selected objects in active collection",
    }
    next_state["ui_state"] = "awaiting_approval"
    _append(next_state, "action_proposal", "Proposed: Move selected objects 2m left")
    _append(next_state, "approval_request", "Preview, apply, or cancel the proposal")
    return next_state


def preview_proposal(session: dict) -> dict:
    next_state = deepcopy(session)
    if not next_state.get("proposal"):
        return next_state

    next_state["ui_state"] = "proposal"
    _append(next_state, "execution_result", "Preview generated for proposal.")
    return next_state


def apply_proposal(session: dict) -> dict:
    next_state = deepcopy(session)
    if not next_state.get("proposal"):
        return next_state

    next_state["ui_state"] = "executing"
    next_state["tool_activity"] = {
        "status": "running",
        "label": "Applying proposal in mock mode",
    }

    _append(next_state, "tool_started", "Applying proposal")
    _append(next_state, "execution_result", "Mock apply complete. No real scene changes made.")
    _append(next_state, "tool_completed", "Proposal apply finished")

    next_state["proposal"] = None
    next_state["ui_state"] = "completed"
    next_state["tool_activity"] = {
        "status": "completed",
        "label": "No active tools",
    }
    return next_state


def cancel_proposal(session: dict) -> dict:
    next_state = deepcopy(session)
    if not next_state.get("proposal"):
        return next_state

    next_state["proposal"] = None
    next_state["ui_state"] = "cancelled"
    _append(next_state, "warning", "Proposal cancelled.")
    return next_state
