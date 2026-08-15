import unittest

from apps.blender_addon.blender_ai_copilot.context.collector import collect_context


class _DummyCollection:
    def __init__(self, name):
        self.name = name


class _DummyMaterial:
    def __init__(self, name):
        self.name = name


class _DummySlot:
    def __init__(self, material):
        self.material = material


class _DummyModifier:
    def __init__(self, name, modifier_type):
        self.name = name
        self.type = modifier_type


class _DummyMesh:
    def __init__(self, vertices=0, edges=0, faces=0):
        self.vertices = [object() for _ in range(vertices)]
        self.edges = [object() for _ in range(edges)]
        self.polygons = [object() for _ in range(faces)]


class _DummyObject(dict):
    def __init__(
        self,
        name,
        obj_type,
        location=(0, 0, 0),
        rotation=(0, 0, 0),
        scale=(1, 1, 1),
        collections=None,
        materials=None,
        modifiers=None,
        mesh=None,
        stable_id=None,
    ):
        super().__init__()
        self.name = name
        self.type = obj_type
        self.location = location
        self.rotation_euler = rotation
        self.scale = scale
        self.users_collection = collections or []
        self.material_slots = [
            _DummySlot(_DummyMaterial(material_name)) for material_name in (materials or [])
        ]
        self.modifiers = [
            _DummyModifier(modifier_name, modifier_type)
            for modifier_name, modifier_type in (modifiers or [])
        ]
        self.data = mesh
        if stable_id:
            self["blender_ai_copilot_id"] = stable_id


class _DummyRender:
    def __init__(self, engine):
        self.engine = engine


class _DummyScene:
    def __init__(self, name, frame_current, engine, objects=None, collections=None):
        self.name = name
        self.frame_current = frame_current
        self.render = _DummyRender(engine)
        self.objects = objects or []
        self.collection = type("CollectionRoot", (), {"children": collections or []})()


class TestContextCollector(unittest.TestCase):
    def test_empty_scene(self):
        scene = _DummyScene("Empty", 1, "BLENDER_EEVEE", objects=[], collections=[])
        result = collect_context(scene, [])

        self.assertEqual(result["scene"]["scene_name"], "Empty")
        self.assertEqual(result["scene"]["object_count"], 0)
        self.assertEqual(result["scene"]["camera_count"], 0)
        self.assertEqual(result["scene"]["light_count"], 0)
        self.assertEqual(result["selection"]["selected_object_ids"], [])

    def test_normal_scene_with_selection(self):
        camera = _DummyObject("Camera", "CAMERA")
        light = _DummyObject("Sun", "LIGHT")
        cube = _DummyObject(
            "Cube",
            "MESH",
            location=(1, 2, 3),
            materials=["Mat_A"],
            modifiers=[("Subsurf", "SUBSURF")],
            mesh=_DummyMesh(vertices=8, edges=12, faces=6),
            stable_id="cube-001",
            collections=[_DummyCollection("Props")],
        )

        scene = _DummyScene(
            "Main",
            24,
            "CYCLES",
            objects=[camera, light, cube],
            collections=[_DummyCollection("Props"), _DummyCollection("Lighting")],
        )

        result = collect_context(scene, [cube])

        self.assertEqual(result["scene"]["object_count"], 3)
        self.assertEqual(result["scene"]["camera_count"], 1)
        self.assertEqual(result["scene"]["light_count"], 1)
        self.assertIn("Props", result["scene"]["collections"])

        self.assertEqual(result["selection"]["selected_object_ids"], ["cube-001"])
        self.assertEqual(result["selection"]["selected_object_names"], ["Cube"])
        self.assertEqual(result["selection"]["selected_object_types"], ["MESH"])

        self.assertEqual(len(result["objects"]), 1)
        self.assertEqual(result["objects"][0]["mesh_stats"]["vertices"], 8)
        self.assertEqual(result["objects"][0]["materials"], ["Mat_A"])
        self.assertEqual(result["objects"][0]["modifiers"][0]["type"], "SUBSURF")

    def test_no_selection_uses_relevant_scene_objects(self):
        a = _DummyObject("A", "EMPTY")
        b = _DummyObject("B", "MESH", mesh=_DummyMesh(vertices=1, edges=1, faces=1))
        scene = _DummyScene("Generic", 10, "BLENDER_EEVEE", objects=[a, b])

        result = collect_context(scene, [])

        self.assertEqual(len(result["objects"]), 2)
        self.assertEqual(result["objects"][0]["name"], "A")
        self.assertEqual(result["objects"][1]["name"], "B")


if __name__ == "__main__":
    unittest.main()
