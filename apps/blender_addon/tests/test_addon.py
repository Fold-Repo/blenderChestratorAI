import importlib
import unittest


class TestAddonShell(unittest.TestCase):
    def test_module_has_metadata_and_lifecycle(self):
        module = importlib.import_module("apps.blender_addon.blender_ai_copilot")

        self.assertIn("name", module.bl_info)
        self.assertTrue(callable(module.register))
        self.assertTrue(callable(module.unregister))

    def test_register_unregister_are_safe_outside_blender(self):
        module = importlib.import_module("apps.blender_addon.blender_ai_copilot")

        module.register()
        module.unregister()

    def test_state_status_badge_text(self):
        state_module = importlib.import_module(
            "apps.blender_addon.blender_ai_copilot.state.store"
        )

        self.assertEqual(state_module.status_badge_text("READY"), "Status: Ready")
        self.assertEqual(
            state_module.status_badge_text("OFFLINE"), "Status: Offline"
        )
        self.assertEqual(
            state_module.status_badge_text("DISABLED"), "Status: Disabled"
        )

    def test_ui_and_config_modules_load_without_blender(self):
        ui_module = importlib.import_module("apps.blender_addon.blender_ai_copilot.ui")
        config_module = importlib.import_module(
            "apps.blender_addon.blender_ai_copilot.config"
        )

        self.assertTrue(callable(ui_module.register))
        self.assertTrue(callable(ui_module.unregister))
        self.assertTrue(callable(config_module.register))
        self.assertTrue(callable(config_module.unregister))


if __name__ == "__main__":
    unittest.main()
