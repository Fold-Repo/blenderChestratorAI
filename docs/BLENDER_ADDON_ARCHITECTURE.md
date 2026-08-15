# Blender Add-on Architecture

## Runtime
Python using Blender's `bpy` API.

## Modules
```text
blender_ai_copilot/
  __init__.py
  manifest/
  ui/
  api/
  context/
  tools/
  policy/
  preview/
  execution/
  auth/
  state/
  telemetry/
  tests/
```

## UI
Use Blender-native panels/operators/properties rather than embedding a separate web runtime in the MVP. This minimizes packaging complexity and keeps the assistant native to Blender.

## Context Collector
Collect only relevant structured information:
- scene metadata
- object identity/type
- transforms
- collection
- materials
- modifiers
- mesh statistics
- active/selected objects
- camera/light summary

Use deterministic collectors, not LLM-generated inspection scripts.

## Tool Executor
Each tool has:
- schema
- permission class
- validator
- executor
- result schema
- audit metadata
- optional rollback strategy

## Undo
Blender operators can participate in Blender's undo system. For multi-step AI actions, create an application-level action record and associate it with the relevant Blender undo checkpoint where practical.

## Compatibility
Target a specific supported Blender major/minor range for the first release instead of claiming universal compatibility. The implementation should isolate version-specific API code behind adapters.

Blender's official documentation confirms that add-ons are Python modules registered through Blender's add-on system and that operators can expose functionality with undo support.
