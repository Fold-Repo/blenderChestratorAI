"""Native Blender panel for Blender AI Copilot MVP-4."""

import json

from ..state import loads_session
from ..state.store import EMPTY_STATE_BODY, EMPTY_STATE_TITLE, status_badge_text


def _icon_for_role(role: str) -> str:
    icons = {
        "user": "USER",
        "assistant": "OUTLINER_OB_FONT",
        "tool_started": "TIME",
        "tool_completed": "CHECKMARK",
        "warning": "ERROR",
        "error": "CANCEL",
        "action_proposal": "MODIFIER",
        "approval_request": "QUESTION",
        "execution_result": "INFO",
    }
    return icons.get(role, "DOT")


def _message_preview(message: dict) -> str:
    timestamp = message.get("timestamp", "")
    short_ts = timestamp[11:19] if len(timestamp) >= 19 else "--:--:--"
    role = str(message.get("role", "message")).replace("_", " ").title()
    content = str(message.get("content", ""))
    if len(content) > 78:
        content = f"{content[:75]}..."
    return f"[{short_ts}] {role}: {content}"

try:
    import bpy  # type: ignore
except ModuleNotFoundError:  # pragma: no cover
    bpy = None


if bpy is not None:
    class BLENDERAICOPILOT_PT_workspace(bpy.types.Panel):
        bl_label = "Blender AI Copilot"
        bl_idname = "BLENDERAICOPILOT_PT_workspace"
        bl_space_type = "VIEW_3D"
        bl_region_type = "UI"
        bl_category = "Copilot"

        def draw(self, context):
            layout = self.layout
            state = context.scene.blender_ai_copilot_state
            session = loads_session(state.conversation_json)
            proposal = session.get("proposal")
            tool_activity = session.get("tool_activity", {})

            header_box = layout.box()
            header_row = header_box.row(align=True)
            header_row.label(text="Copilot Workspace")
            header_row.operator(
                "blender_ai_copilot.open_settings", text="", icon="PREFERENCES"
            )

            status_box = layout.box()
            status_box.label(text=status_badge_text(state.panel_status), icon="INFO")
            status_box.label(text=f"Conversation: {state.ui_state}")
            status_box.operator(
                "blender_ai_copilot.refresh_connection",
                text="Refresh Connection",
                icon="FILE_REFRESH",
            )

            if state.backend_project_id:
                status_box.label(text=f"Project: {state.backend_project_id}")
            if state.backend_conversation_id:
                status_box.label(text=f"Conversation ID: {state.backend_conversation_id}")

            context_box = layout.box()
            context_box.label(text="Scene Context", icon="SCENE_DATA")
            context_box.operator(
                "blender_ai_copilot.refresh_scene_context",
                text="Refresh Scene Context",
                icon="FILE_REFRESH",
            )

            collected_context = {}
            if state.context_json:
                try:
                    collected_context = json.loads(state.context_json)
                except json.JSONDecodeError:
                    collected_context = {}

            scene_context = collected_context.get("scene", {})
            selection_context = collected_context.get("selection", {})
            context_box.label(text=f"Scene: {scene_context.get('scene_name', context.scene.name)}")
            context_box.label(text=f"Frame: {scene_context.get('frame', context.scene.frame_current)}")
            context_box.label(text=f"Render: {scene_context.get('render_engine', context.scene.render.engine)}")
            context_box.label(text=f"Objects: {scene_context.get('object_count', len(context.scene.objects))}")
            context_box.label(text=f"Cameras: {scene_context.get('camera_count', 0)}")
            context_box.label(text=f"Lights: {scene_context.get('light_count', 0)}")

            collections = scene_context.get("collections", [])
            if collections:
                context_box.label(text=f"Collections: {', '.join(collections[:4])}")

            selected_ids = selection_context.get("selected_object_ids", [])
            context_box.label(text=f"Selected IDs: {len(selected_ids)}")
            if selected_ids:
                context_box.label(text=f"Top Selection: {selected_ids[0]}")

            if state.context_collected_at:
                context_box.label(text=f"Collected: {state.context_collected_at[11:19]}")

            conversation_box = layout.box()
            conversation_box.label(text="Conversation", icon="TEXT")

            messages = session.get("messages", [])
            if not messages:
                conversation_box.label(text=EMPTY_STATE_TITLE, icon="OUTLINER_OB_FONT")
                conversation_box.label(text=EMPTY_STATE_BODY)
            else:
                for message in messages[-10:]:
                    conversation_box.label(
                        text=_message_preview(message),
                        icon=_icon_for_role(message.get("role", "")),
                    )

            if state.last_error:
                error_box = layout.box()
                error_box.label(text="Error State", icon="CANCEL")
                error_box.label(text=state.last_error)

            tool_box = layout.box()
            tool_box.label(text="Tool Activity", icon="TOOL_SETTINGS")
            tool_box.label(text=f"Status: {tool_activity.get('status', 'idle')}")
            tool_box.label(text=str(tool_activity.get("label", "No active tools")))

            proposal_box = layout.box()
            proposal_box.label(text="Action Proposal", icon="MODIFIER")
            if proposal:
                proposal_box.label(text=f"Change: {proposal.get('change', 'n/a')}")
                proposal_box.label(text=f"Targets: {', '.join(proposal.get('targets', []))}")
                proposal_box.label(text=f"Parameters: {proposal.get('parameters', 'n/a')}")
                proposal_box.label(text=f"Risk: {proposal.get('risk', 'n/a')}")
                proposal_box.label(text=f"Scene Area: {proposal.get('scene_area', 'n/a')}")

                if proposal.get("source") == "agent":
                    proposal_box.label(
                        text="Preview before applying. Approval is explicit.",
                        icon="QUESTION",
                    )
                    approval_row = proposal_box.row(align=True)
                    approval_row.operator(
                        "blender_ai_copilot.preview_proposal", text="Preview", icon="HIDE_OFF"
                    )
                    approval_row.operator(
                        "blender_ai_copilot.apply_proposal", text="Apply", icon="CHECKMARK"
                    )
                    approval_row.operator(
                        "blender_ai_copilot.cancel_proposal", text="Cancel", icon="CANCEL"
                    )
                else:
                    approval_row = proposal_box.row(align=True)
                    approval_row.operator(
                        "blender_ai_copilot.preview_proposal", text="Preview", icon="HIDE_OFF"
                    )
                    approval_row.operator(
                        "blender_ai_copilot.apply_proposal", text="Apply", icon="CHECKMARK"
                    )
                    approval_row.operator(
                        "blender_ai_copilot.cancel_proposal", text="Cancel", icon="CANCEL"
                    )
            else:
                proposal_box.label(text="No active proposal")
                proposal_box.operator(
                    "blender_ai_copilot.seed_proposal", text="Create Mock Proposal", icon="ADD"
                )

            undo_row = proposal_box.row()
            undo_row.operator(
                "blender_ai_copilot.undo_last_action", text="Undo Last Copilot Action", icon="LOOP_BACK"
            )
            undo_row.enabled = bool(session.get("undo_available"))

            composer_box = layout.box()
            composer_box.label(text="Composer")
            composer_box.prop(state, "composer_text", text="")

            action_row = composer_box.row(align=True)
            action_row.operator(
                "blender_ai_copilot.send_message", text="Send", icon="PLAY"
            )
            action_row.operator("blender_ai_copilot.cancel_current", text="Cancel", icon="X")

            retry_row = composer_box.row(align=True)
            retry_row.operator("blender_ai_copilot.retry_last", text="Retry", icon="FILE_REFRESH")
            retry_row.enabled = state.can_retry

            clear_row = composer_box.row(align=True)
            clear_row.operator(
                "blender_ai_copilot.clear_conversation", text="Clear", icon="TRASH"
            )


    classes = (BLENDERAICOPILOT_PT_workspace,)


    def register():
        for cls in classes:
            bpy.utils.register_class(cls)


    def unregister():
        for cls in reversed(classes):
            bpy.utils.unregister_class(cls)

else:
    classes = tuple()

    def register():
        return None

    def unregister():
        return None
