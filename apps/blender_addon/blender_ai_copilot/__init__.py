"""Blender AI Copilot add-on package for MVP-1 shell."""

bl_info = {
    "name": "Blender AI Copilot",
    "author": "Blender AI Copilot Team",
    "version": (0, 9, 0),
    "blender": (4, 2, 0),
    "location": "View3D > Sidebar > Copilot",
    "description": "Native Blender Copilot with authenticated scene tools, proposals, and undo.",
    "category": "3D View",
}

from .config import register as register_config
from .config import unregister as unregister_config
from .state import register as register_state
from .state import unregister as unregister_state
from .ui import register as register_ui
from .ui import unregister as unregister_ui


def register():
    register_config()
    register_state()
    register_ui()


def unregister():
    unregister_ui()
    unregister_state()
    unregister_config()
