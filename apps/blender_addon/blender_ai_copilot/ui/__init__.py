"""UI package exports for Blender AI Copilot."""

from . import operators, panels


def register():
    operators.register()
    panels.register()


def unregister():
    panels.unregister()
    operators.unregister()
