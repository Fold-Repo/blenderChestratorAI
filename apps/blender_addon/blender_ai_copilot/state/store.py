"""UI state model for Blender AI Copilot MVP-4 shell."""

from .chat_logic import UI_STATES, default_session, dumps_session

PANEL_STATUS_ITEMS = [
    ("READY", "Ready", "Copilot is ready"),
    ("OFFLINE", "Offline", "Backend is unavailable"),
    ("DISABLED", "Disabled", "Copilot is disabled"),
]

EMPTY_STATE_TITLE = "Start a Copilot conversation"
EMPTY_STATE_BODY = "Send a message to begin. AI and backend connectivity arrive in later MVP phases."

UI_STATE_ITEMS = [
    ("idle", "Idle", "Copilot is idle"),
    ("thinking", "Thinking", "Copilot is preparing a response"),
    ("tool_running", "Tool Running", "A mock tool is running"),
    ("proposal", "Proposal", "A proposal preview is shown"),
    ("awaiting_approval", "Awaiting Approval", "Waiting for user approval"),
    ("executing", "Executing", "Applying approved action"),
    ("completed", "Completed", "Last action completed"),
    ("error", "Error", "Last action failed"),
    ("cancelled", "Cancelled", "Action cancelled"),
]

DEFAULT_SESSION_JSON = dumps_session(default_session())


def status_badge_text(status: str) -> str:
    mapping = {
        "READY": "Status: Ready",
        "OFFLINE": "Status: Offline",
        "DISABLED": "Status: Disabled",
    }
    return mapping.get(status, "Status: Unknown")


try:
    import bpy  # type: ignore
except ModuleNotFoundError:  # pragma: no cover
    bpy = None


if bpy is not None:
    class BlenderAICopilotState(bpy.types.PropertyGroup):
        panel_status: bpy.props.EnumProperty(
            name="Status",
            description="Current shell status in the Copilot panel",
            items=PANEL_STATUS_ITEMS,
            default="READY",
        )

        composer_text: bpy.props.StringProperty(
            name="Message",
            description="Composer input for upcoming chat phases",
            default="",
        )

        ui_state: bpy.props.EnumProperty(
            name="Conversation State",
            description="Current local chat state",
            items=UI_STATE_ITEMS,
            default="idle",
        )

        last_error: bpy.props.StringProperty(
            name="Last Error",
            description="Most recent local mock error",
            default="",
        )

        can_retry: bpy.props.BoolProperty(
            name="Can Retry",
            description="Indicates whether retry is available",
            default=False,
        )

        conversation_json: bpy.props.StringProperty(
            name="Conversation JSON",
            description="Serialized local conversation store for MVP-2",
            default=DEFAULT_SESSION_JSON,
        )

        backend_project_id: bpy.props.StringProperty(
            name="Backend Project ID",
            description="Current backend project ID for conversation routing",
            default="",
        )

        backend_conversation_id: bpy.props.StringProperty(
            name="Backend Conversation ID",
            description="Current backend conversation ID",
            default="",
        )

        context_json: bpy.props.StringProperty(
            name="Scene Context JSON",
            description="Serialized deterministic scene context",
            default="{}",
        )

        context_collected_at: bpy.props.StringProperty(
            name="Context Collected At",
            description="ISO timestamp for latest context collection",
            default="",
        )


    classes = (BlenderAICopilotState,)


    def register():
        for cls in classes:
            bpy.utils.register_class(cls)

        bpy.types.Scene.blender_ai_copilot_state = bpy.props.PointerProperty(
            type=BlenderAICopilotState
        )


    def unregister():
        if hasattr(bpy.types.Scene, "blender_ai_copilot_state"):
            del bpy.types.Scene.blender_ai_copilot_state

        for cls in reversed(classes):
            bpy.utils.unregister_class(cls)

else:
    classes = tuple()

    def register():
        return None

    def unregister():
        return None
