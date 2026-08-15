import unittest

from apps.blender_addon.blender_ai_copilot.tools import (
    PermissionLevel,
    ToolExecutionContext,
    create_tool_executor,
    execute_approved_transform,
    preview_transform_proposal,
)


class _Object(dict):
    def __init__(self, name, obj_type, collections=(), object_id=None):
        super().__init__()
        self.name = name
        self.type = obj_type
        self.location = (1, 2, 3)
        self.rotation_euler = (0, 0, 0)
        self.scale = (1, 1, 1)
        self.users_collection = [type("Collection", (), {"name": item})() for item in collections]
        self.material_slots = []
        self.modifiers = []
        self.data = None
        self.selected = False
        if object_id:
            self["blender_ai_copilot_id"] = object_id

    def select_set(self, selected):
        self.selected = selected


class _Scene:
    name = "Demo"
    frame_current = 1
    render = type("Render", (), {"engine": "BLENDER_EEVEE"})()
    collection = type("Root", (), {"children": []})()

    def __init__(self, objects):
        self.objects = objects


class TestMvp5Tools(unittest.TestCase):
    def setUp(self):
        self.tree = _Object("Tree Oak", "MESH", ("Nature",), "tree-1")
        self.rock = _Object("Rock", "MESH", ("Nature",), "rock-1")
        self.camera = _Object("Camera", "CAMERA", object_id="camera-1")
        self.scene = _Scene([self.tree, self.rock, self.camera])
        self.context = ToolExecutionContext(self.scene, [self.tree], "project-1", "Demo")
        self.executor = create_tool_executor()

    def test_registry_has_versioned_permissions(self):
        definitions = {item.name: item for item in self.executor.registry.list()}
        self.assertEqual(definitions["find_objects"].version, "1")
        self.assertEqual(definitions["select_objects"].permission_level, PermissionLevel.SAFE_WRITE)
        self.assertEqual(definitions["modify_object_transform"].permission_level, PermissionLevel.APPROVAL_REQUIRED)

    def test_read_only_tools_return_deterministic_results(self):
        summary = self.executor.execute("get_scene_summary", {}, self.context)
        found = self.executor.execute("find_objects", {"contains": "tree"}, self.context)
        selected = self.executor.execute("get_selected_objects", {}, self.context)
        self.assertEqual(summary["result"]["scene"]["object_count"], 3)
        self.assertEqual(found["result"]["count"], 1)
        self.assertEqual(found["result"]["objects"][0]["id"], "tree-1")
        self.assertEqual(selected["result"]["objects"][0]["id"], "tree-1")

    def test_select_validates_all_ids_before_mutating(self):
        rejected = self.executor.execute("select_objects", {"object_ids": ["tree-1", "missing"]}, self.context)
        self.assertFalse(rejected["ok"])
        self.assertEqual(rejected["error"]["code"], "UNKNOWN_OBJECT_ID")
        self.assertFalse(self.tree.selected)
        accepted = self.executor.execute("select_objects", {"object_ids": ["tree-1", "rock-1"]}, self.context)
        self.assertTrue(accepted["ok"])
        self.assertTrue(self.tree.selected)
        self.assertTrue(self.rock.selected)
        self.assertEqual(accepted["audit"]["project_id"], "project-1")

    def test_invalid_arguments_and_scene_scope_are_rejected(self):
        invalid = self.executor.execute("find_objects", {}, self.context)
        wrong_scope = self.executor.execute("get_scene_summary", {}, ToolExecutionContext(self.scene, [], expected_scene_name="Other"))
        self.assertEqual(invalid["error"]["code"], "INVALID_ARGUMENTS")
        self.assertEqual(wrong_scope["error"]["code"], "SCENE_SCOPE_MISMATCH")

    def test_transform_cannot_execute_without_approval(self):
        result = self.executor.execute(
            "modify_object_transform",
            {"object_ids": ["tree-1"], "location_delta": [-2, 0, 0]},
            self.context,
        )
        self.assertFalse(result["ok"])
        self.assertEqual(result["error"]["code"], "APPROVAL_REQUIRED")

    def test_approved_transform_previews_executes_and_revalidates_targets(self):
        proposal = {
            "proposal_id": "proposal-1",
            "execution_arguments": {
                "object_ids": ["tree-1"],
                "location_delta": [-2, 0, 0],
                "rotation_delta": [0, 0, 0],
                "scale_multiplier": [1, 1, 1],
            },
        }
        preview = preview_transform_proposal(proposal, self.context)
        self.assertEqual(preview["targets"][0]["after"]["location"], [-1.0, 2.0, 3.0])
        result = execute_approved_transform(proposal, self.context)
        self.assertTrue(result["ok"])
        self.assertEqual(self.tree.location, [-1.0, 2.0, 3.0])

        stale = execute_approved_transform(
            {
                "proposal_id": "proposal-2",
                "execution_arguments": {"object_ids": ["missing"], "location_delta": [-2, 0, 0]},
            },
            self.context,
        )
        self.assertFalse(stale["ok"])
        self.assertEqual(stale["error"]["code"], "UNKNOWN_OBJECT_ID")

    def test_transform_proposal_arguments_are_bounded(self):
        invalid = self.executor.execute(
            "modify_object_transform",
            {"object_ids": ["tree-1"], "scale_multiplier": [0, 1, 1]},
            self.context,
        )
        self.assertEqual(invalid["error"]["code"], "INVALID_ARGUMENTS")
