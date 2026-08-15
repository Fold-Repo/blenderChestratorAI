"""UI operators for Blender AI Copilot MVP-4 shell."""

import json
from datetime import datetime, timezone

from ..api import BackendClient, BackendClientError
from ..context import collect_context
from ..tools import (
    ToolExecutionContext,
    execute_approved_transform,
    preview_transform_proposal,
)
from ..tools.contracts import ToolValidationError
from ..state import (
    apply_proposal,
    await_agent_proposal,
    begin_backend_turn,
    cancel_current,
    cancel_proposal,
    complete_backend_turn,
    clear_conversation,
    complete_agent_execution,
    dumps_session,
    fail_backend_turn,
    loads_session,
    preview_proposal,
    preview_agent_proposal,
    record_undo,
    seed_mock_proposal,
)


def _save_session(state, session: dict) -> None:
    state.conversation_json = dumps_session(session)
    state.ui_state = session.get("ui_state", "idle")
    state.last_error = session.get("last_error", "")
    state.can_retry = session.get("can_retry", False)


def _backend_client_from_context(context):
    addon = context.preferences.addons.get("blender_ai_copilot")
    prefs = addon.preferences if addon else None

    base_url = getattr(prefs, "backend_base_url", "http://localhost:3009")
    timeout_seconds = float(getattr(prefs, "request_timeout_seconds", 4.0))
    retry_attempts = int(getattr(prefs, "request_retry_count", 1))
    auth_token = getattr(prefs, "auth_token", "")
    return BackendClient(
        base_url,
        timeout_seconds=timeout_seconds,
        retry_attempts=retry_attempts,
        auth_token=auth_token or None,
    )


def _capture_scene_context(context) -> dict:
    scene_context = collect_context(context.scene, list(context.selected_objects))
    state = context.scene.blender_ai_copilot_state
    state.context_json = json.dumps(scene_context)
    state.context_collected_at = datetime.now(timezone.utc).isoformat()
    return scene_context


def _tool_context_from_context(context, state) -> ToolExecutionContext:
    return ToolExecutionContext(
        scene=context.scene,
        selected_objects=list(context.selected_objects),
        project_id=state.backend_project_id or None,
        expected_scene_name=context.scene.name,
    )


def _ensure_backend_session(state, client: BackendClient):
    project_id = state.backend_project_id
    if not project_id:
        project = client.create_project("Blender Workspace")
        project_id = project.get("id", "")
        state.backend_project_id = project_id

    conversation_id = state.backend_conversation_id
    if not conversation_id:
        conversation = client.create_conversation(project_id)
        conversation_id = conversation.get("id", "")
        state.backend_conversation_id = conversation_id

    return conversation_id


def _post_audit_log(context, action: str, **kwargs) -> None:
    try:
        copilot_state = context.scene.blender_ai_copilot_state
        project_id = copilot_state.backend_project_id
        if not project_id:
            return
        client = _backend_client_from_context(context)
        client.create_audit_log(project_id=project_id, action=action, **kwargs)
    except Exception:
        return


def _send_message_to_backend(context, message: str):
    copilot_state = context.scene.blender_ai_copilot_state
    session = loads_session(copilot_state.conversation_json)
    session = begin_backend_turn(session, message)

    try:
        client = _backend_client_from_context(context)
        conversation_id = _ensure_backend_session(copilot_state, client)
        scene_context = _capture_scene_context(context)
        run = client.create_run(conversation_id, message, scene_context)
        assistant_text = run.get("assistantMessage") or "Backend returned an empty message."
        _post_audit_log(
            context,
            "send_message",
            parameters_metadata={
                "runId": run.get("id"),
                "toolCallsCount": len(run.get("toolCalls") or []),
            },
            approval_required=bool(run.get("proposal")),
            approved=False,
            execution_result=run.get("status"),
        )

        if run.get("proposal"):
            session = await_agent_proposal(
                session,
                assistant_text,
                run["proposal"],
                tool_calls=run.get("toolCalls", []),
            )
        else:
            session = complete_backend_turn(
                session,
                assistant_text,
                tool_calls=run.get("toolCalls", []),
            )
        copilot_state.panel_status = "READY"
    except BackendClientError as exc:
        session = fail_backend_turn(session, str(exc))
        copilot_state.panel_status = "OFFLINE"

    _save_session(copilot_state, session)

try:
    import bpy  # type: ignore
except ModuleNotFoundError:  # pragma: no cover
    bpy = None


if bpy is not None:
    class BLENDERAICOPILOT_OT_open_settings(bpy.types.Operator):
        bl_idname = "blender_ai_copilot.open_settings"
        bl_label = "Open Copilot Settings"
        bl_description = "Open Blender preferences to Blender AI Copilot settings"

        def execute(self, context):  # noqa: ARG002
            bpy.ops.screen.userpref_show("INVOKE_DEFAULT")
            bpy.ops.preferences.addon_show(module="blender_ai_copilot")
            return {"FINISHED"}


    class BLENDERAICOPILOT_OT_login(bpy.types.Operator):
        bl_idname = "blender_ai_copilot.login"
        bl_label = "Authenticate"
        bl_description = "Log in or register with the backend"

        def execute(self, context):
            addon = context.preferences.addons.get("blender_ai_copilot")
            prefs = addon.preferences if addon else None
            if not prefs:
                self.report({"ERROR"}, "Add-on preferences not found.")
                return {"CANCELLED"}

            username = prefs.username.strip()
            password = prefs.password.strip()
            if not username or not password:
                self.report({"WARNING"}, "Enter username and password.")
                return {"CANCELLED"}

            client = BackendClient(
                prefs.backend_base_url,
                timeout_seconds=float(prefs.request_timeout_seconds),
                retry_attempts=int(prefs.request_retry_count),
            )
            try:
                try:
                    response = client.login(username, password)
                except BackendClientError:
                    response = client.register(
                        username, f"{username}@example.com", password
                    )

                token = response.get("token", "")
                if token:
                    prefs.auth_token = token
                    self.report({"INFO"}, "Log in successful.")
                else:
                    self.report({"ERROR"}, "Login failed: No token received.")
                    return {"CANCELLED"}
            except BackendClientError as exc:
                self.report({"ERROR"}, f"Authentication failed: {exc}")
                return {"CANCELLED"}
            return {"FINISHED"}


    class BLENDERAICOPILOT_OT_send_message(bpy.types.Operator):
        bl_idname = "blender_ai_copilot.send_message"
        bl_label = "Send"
        bl_description = "Send a backend-connected message"

        def execute(self, context):
            copilot_state = context.scene.blender_ai_copilot_state
            message = copilot_state.composer_text
            if not message.strip():
                self.report({"WARNING"}, "Enter a message before sending.")
                return {"CANCELLED"}

            _send_message_to_backend(context, message)
            copilot_state.composer_text = ""
            return {"FINISHED"}


    class BLENDERAICOPILOT_OT_retry_last(bpy.types.Operator):
        bl_idname = "blender_ai_copilot.retry_last"
        bl_label = "Retry"
        bl_description = "Retry the last failed backend action"

        def execute(self, context):
            copilot_state = context.scene.blender_ai_copilot_state
            session = loads_session(copilot_state.conversation_json)
            if not session.get("can_retry"):
                return {"CANCELLED"}

            retry_message = session.get("last_user_message", "")
            if not retry_message:
                return {"CANCELLED"}

            _send_message_to_backend(context, retry_message)
            return {"FINISHED"}


    class BLENDERAICOPILOT_OT_clear_conversation(bpy.types.Operator):
        bl_idname = "blender_ai_copilot.clear_conversation"
        bl_label = "Clear"
        bl_description = "Clear the local conversation"

        def execute(self, context):
            copilot_state = context.scene.blender_ai_copilot_state
            session = loads_session(copilot_state.conversation_json)
            session = clear_conversation(session)
            copilot_state.backend_conversation_id = ""
            _save_session(copilot_state, session)
            return {"FINISHED"}


    class BLENDERAICOPILOT_OT_refresh_connection(bpy.types.Operator):
        bl_idname = "blender_ai_copilot.refresh_connection"
        bl_label = "Refresh Connection"
        bl_description = "Check backend availability and update connection status"

        def execute(self, context):
            copilot_state = context.scene.blender_ai_copilot_state
            try:
                client = _backend_client_from_context(context)
                client.health()
                copilot_state.panel_status = "READY"
                self.report({"INFO"}, "Backend connection is healthy.")
            except BackendClientError as exc:
                copilot_state.panel_status = "OFFLINE"
                self.report({"WARNING"}, f"Backend unavailable: {exc}")

            return {"FINISHED"}


    class BLENDERAICOPILOT_OT_refresh_scene_context(bpy.types.Operator):
        bl_idname = "blender_ai_copilot.refresh_scene_context"
        bl_label = "Refresh Scene Context"
        bl_description = "Collect deterministic scene context from Blender"

        def execute(self, context):
            _capture_scene_context(context)
            self.report({"INFO"}, "Scene context collected.")
            return {"FINISHED"}


    class BLENDERAICOPILOT_OT_cancel_current(bpy.types.Operator):
        bl_idname = "blender_ai_copilot.cancel_current"
        bl_label = "Cancel"
        bl_description = "Cancel current local operation"

        def execute(self, context):
            copilot_state = context.scene.blender_ai_copilot_state
            session = loads_session(copilot_state.conversation_json)
            session = cancel_current(session)
            _save_session(copilot_state, session)
            return {"FINISHED"}


    class BLENDERAICOPILOT_OT_seed_proposal(bpy.types.Operator):
        bl_idname = "blender_ai_copilot.seed_proposal"
        bl_label = "Mock Proposal"
        bl_description = "Add a mock action proposal"

        def execute(self, context):
            copilot_state = context.scene.blender_ai_copilot_state
            session = loads_session(copilot_state.conversation_json)
            session = seed_mock_proposal(session)
            _save_session(copilot_state, session)
            return {"FINISHED"}


    class BLENDERAICOPILOT_OT_preview_proposal(bpy.types.Operator):
        bl_idname = "blender_ai_copilot.preview_proposal"
        bl_label = "Preview"
        bl_description = "Preview proposal without changing the scene"

        def execute(self, context):
            copilot_state = context.scene.blender_ai_copilot_state
            session = loads_session(copilot_state.conversation_json)
            proposal = session.get("proposal")
            if proposal and proposal.get("source") == "agent":
                try:
                    preview = preview_transform_proposal(
                        proposal, _tool_context_from_context(context, copilot_state)
                    )
                    session = preview_agent_proposal(session, preview)
                    _post_audit_log(
                        context,
                        "preview",
                        tool="modify_object_transform",
                        parameters_metadata={"targetsCount": len(preview.get("targets", []))},
                        approval_required=True,
                        approved=False,
                        execution_result="success",
                    )
                except ToolValidationError as exc:
                    session = fail_backend_turn(session, exc.message)
            else:
                session = preview_proposal(session)
            _save_session(copilot_state, session)
            return {"FINISHED"}


    class BLENDERAICOPILOT_OT_apply_proposal(bpy.types.Operator):
        bl_idname = "blender_ai_copilot.apply_proposal"
        bl_label = "Apply"
        bl_description = "Apply an approved proposal"
        bl_options = {"REGISTER", "UNDO"}

        def execute(self, context):
            copilot_state = context.scene.blender_ai_copilot_state
            session = loads_session(copilot_state.conversation_json)
            proposal = session.get("proposal")
            if proposal and proposal.get("source") == "agent":
                try:
                    result = execute_approved_transform(
                        proposal, _tool_context_from_context(context, copilot_state)
                    )
                    if result.get("ok"):
                        session = complete_agent_execution(session, result.get("result", {}))
                        _post_audit_log(
                            context,
                            "apply",
                            tool="modify_object_transform",
                            parameters_metadata={
                                "targetsCount": result.get("result", {}).get("count", 0)
                            },
                            approval_required=True,
                            approved=True,
                            execution_result="success",
                        )
                    else:
                        error_msg = result.get("error", {}).get("message", "Transform execution failed.")
                        session = fail_backend_turn(session, error_msg)
                        _post_audit_log(
                            context,
                            "apply",
                            tool="modify_object_transform",
                            parameters_metadata={},
                            approval_required=True,
                            approved=True,
                            execution_result=f"failed: {error_msg}",
                        )
                except ToolValidationError as exc:
                    session = fail_backend_turn(session, exc.message)
            else:
                session = apply_proposal(session)
            _save_session(copilot_state, session)
            return {"FINISHED"}


    class BLENDERAICOPILOT_OT_undo_last_action(bpy.types.Operator):
        bl_idname = "blender_ai_copilot.undo_last_action"
        bl_label = "Undo Copilot Action"
        bl_description = "Undo the last approved Copilot transform"

        def execute(self, context):
            copilot_state = context.scene.blender_ai_copilot_state
            session = loads_session(copilot_state.conversation_json)
            if not session.get("undo_available"):
                return {"CANCELLED"}
            bpy.ops.ed.undo()
            _post_audit_log(
                context,
                "undo",
                tool="modify_object_transform",
                parameters_metadata={},
                approval_required=True,
                approved=True,
                execution_result="undone",
            )
            _save_session(copilot_state, record_undo(session))
            return {"FINISHED"}


    class BLENDERAICOPILOT_OT_cancel_proposal(bpy.types.Operator):
        bl_idname = "blender_ai_copilot.cancel_proposal"
        bl_label = "Cancel Proposal"
        bl_description = "Cancel current mock proposal"

        def execute(self, context):
            copilot_state = context.scene.blender_ai_copilot_state
            session = loads_session(copilot_state.conversation_json)
            _post_audit_log(
                context,
                "cancel",
                tool="modify_object_transform",
                parameters_metadata={},
                approval_required=True,
                approved=False,
                execution_result="cancelled",
            )
            session = cancel_proposal(session)
            _save_session(copilot_state, session)
            return {"FINISHED"}


    classes = (
        BLENDERAICOPILOT_OT_open_settings,
        BLENDERAICOPILOT_OT_login,
        BLENDERAICOPILOT_OT_send_message,
        BLENDERAICOPILOT_OT_retry_last,
        BLENDERAICOPILOT_OT_refresh_connection,
        BLENDERAICOPILOT_OT_refresh_scene_context,
        BLENDERAICOPILOT_OT_clear_conversation,
        BLENDERAICOPILOT_OT_cancel_current,
        BLENDERAICOPILOT_OT_seed_proposal,
        BLENDERAICOPILOT_OT_preview_proposal,
        BLENDERAICOPILOT_OT_apply_proposal,
        BLENDERAICOPILOT_OT_undo_last_action,
        BLENDERAICOPILOT_OT_cancel_proposal,
    )


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
