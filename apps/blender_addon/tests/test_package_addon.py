import importlib.util
import os
import tempfile
import unittest
import zipfile
from pathlib import Path


def _load_package_addon():
    script_path = Path(__file__).resolve().parents[3] / "scripts" / "package_addon.py"
    spec = importlib.util.spec_from_file_location("package_addon", script_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class TestPackageAddon(unittest.TestCase):
    def test_packages_addon_without_pycache(self):
        package_addon = _load_package_addon().package_addon

        with tempfile.TemporaryDirectory() as tmp:
            zip_path = os.path.join(tmp, "blender_ai_copilot.zip")
            packaged = package_addon(zip_path)
            self.assertTrue(os.path.isfile(packaged))

            with zipfile.ZipFile(packaged) as archive:
                names = archive.namelist()

        self.assertIn("blender_ai_copilot/__init__.py", names)
        self.assertTrue(
            any(name.startswith("blender_ai_copilot/api/") for name in names)
        )
        self.assertFalse(any("__pycache__" in name for name in names))
        self.assertFalse(any(name.endswith(".pyc") for name in names))


if __name__ == "__main__":
    unittest.main()
