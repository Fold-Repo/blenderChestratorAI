#!/usr/bin/env python3
"""Bundle the Blender add-on into a release zip."""

from __future__ import annotations

import os
import zipfile

SKIP_DIRS = {"__pycache__", ".git", ".github", ".mypy_cache", ".pytest_cache"}
SKIP_FILES = {".pyc", ".pyo", ".DS_Store"}


def package_addon(output_path: str | None = None) -> str:
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    addon_dir = os.path.join(root_dir, "apps", "blender_addon", "blender_ai_copilot")
    zip_path = output_path or os.path.join(
        root_dir, "apps", "blender_addon", "blender_ai_copilot.zip"
    )

    if not os.path.isdir(addon_dir):
        raise FileNotFoundError(f"Add-on directory not found: {addon_dir}")

    os.makedirs(os.path.dirname(zip_path), exist_ok=True)
    if os.path.exists(zip_path):
        os.remove(zip_path)

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for root, dirs, files in os.walk(addon_dir):
            dirs[:] = [directory for directory in dirs if directory not in SKIP_DIRS]
            for file in files:
                if file.endswith(tuple(SKIP_FILES)) or file in SKIP_FILES:
                    continue
                file_path = os.path.join(root, file)
                rel_path = os.path.join(
                    "blender_ai_copilot", os.path.relpath(file_path, addon_dir)
                )
                zip_file.write(file_path, rel_path)

    return zip_path


if __name__ == "__main__":
    packaged = package_addon()
    print(f"Addon packaged successfully: {packaged}")
