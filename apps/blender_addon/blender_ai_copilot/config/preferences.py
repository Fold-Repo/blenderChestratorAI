"""Add-on preferences and configuration for MVP-9."""

try:
    import bpy  # type: ignore
except ModuleNotFoundError:  # pragma: no cover
    bpy = None


if bpy is not None:
    class BlenderAICopilotAddonPreferences(bpy.types.AddonPreferences):
        bl_idname = "blender_ai_copilot"

        backend_base_url: bpy.props.StringProperty(
            name="Backend Base URL",
            description="Backend endpoint for API connection",
            default="http://localhost:3009",
        )

        request_timeout_seconds: bpy.props.FloatProperty(
            name="Request Timeout (sec)",
            description="HTTP timeout for backend requests",
            default=4.0,
            min=1.0,
            max=30.0,
        )

        request_retry_count: bpy.props.IntProperty(
            name="Retry Count",
            description="Number of retries after initial backend request failure",
            default=1,
            min=0,
            max=5,
        )

        show_status_badge: bpy.props.BoolProperty(
            name="Show Status Badge",
            description="Display status badge in the Copilot panel header",
            default=True,
        )

        username: bpy.props.StringProperty(
            name="Username",
            description="Backend username",
            default="",
        )

        password: bpy.props.StringProperty(
            name="Password",
            description="Backend password",
            default="",
            subtype="PASSWORD",
        )

        auth_token: bpy.props.StringProperty(
            name="Auth Token",
            description="Active session JWT or token",
            default="",
        )

        def draw(self, context):  # noqa: ARG002
            layout = self.layout
            layout.label(text="Blender AI Copilot Settings", icon="PREFERENCES")

            col = layout.column(align=True)
            col.prop(self, "backend_base_url")
            col.prop(self, "request_timeout_seconds")
            col.prop(self, "request_retry_count")
            col.prop(self, "show_status_badge")

            layout.separator()

            layout.label(text="User Authentication", icon="USER")
            col_auth = layout.column(align=True)
            col_auth.prop(self, "username")
            col_auth.prop(self, "password")

            layout.operator(
                "blender_ai_copilot.login",
                text="Authenticate / Log In",
                icon="KEY_DECORATED",
            )

            if self.auth_token:
                box = layout.box()
                box.label(text="Authentication Status: Logged In", icon="CHECKMARK")
                display_token = (
                    f"{self.auth_token[:15]}..."
                    if len(self.auth_token) > 15
                    else self.auth_token
                )
                box.label(text=f"Active Session: {display_token}")
            else:
                box = layout.box()
                box.label(text="Authentication Status: Not Authenticated", icon="ERROR")


    classes = (BlenderAICopilotAddonPreferences,)


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
