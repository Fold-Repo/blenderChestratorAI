# Blender Add-on (MVP-9)

This package contains the Blender-native add-on, safe proposal system, execution workflow, and authenticated backend client required through MVP-9.

## Supported Blender version

Blender 4.2 and newer (`bl_info.blender = (4, 2, 0)`).

## Install (release zip)

```bash
python3 scripts/package_addon.py
```

1. Open Blender.
2. Go to **Edit > Preferences > Add-ons**.
3. Use **Install...** and select `apps/blender_addon/blender_ai_copilot.zip`.
4. Enable **Blender AI Copilot**.
5. Open **3D View > Sidebar > Copilot**.
6. In add-on preferences, enter username/password and click **Authenticate / Log In**.

## Scope

MVP-9 additionally includes:

- username/password preferences and session token storage
- `Authorization: Bearer` on backend requests
- audit events for preview, apply, cancel, and undo
- release packaging script

MVP-8 additionally includes:

- backend-originated transform proposals shown as approval-required
- local validation of bounded transform-proposal arguments
- transform modification execution, approval completion, preview, and undo support

MVP-5 additionally includes:

- versioned allow-listed tool registry and executor
- strict argument, object-ID, permission, and active-scene validation
- deterministic `get_scene_summary`, `get_selected_objects`, `find_objects`, and `select_objects` tools
- structured result/error envelopes and audit metadata
- an approval-required `modify_object_transform` contract

MVP-4 includes:

- add-on metadata and registration lifecycle
- Copilot workspace panel in the 3D View sidebar
- header with settings entry point
- backend API client with timeout and retry configuration
- backend connection status indicator and refresh action
- request handling and JSON response parsing
- project and conversation routing IDs in state
- conversation create + run create integration
- Blender to backend to Blender message loop
- deterministic scene context collector
- scene summary context (scene/frame/engine/object-camera-light counts/collections)
- object detail context (id/type/transforms/materials/modifiers/mesh stats)
- selection context (selected IDs/names/types/transforms)
- manual context refresh and context-aware run payloads
- tool activity placeholder
- action proposal placeholder with preview/apply/cancel controls
- module separation for UI, state, and configuration

Out of scope in MVP-9:

- persistent login across backend restarts
- SSO / OAuth
- BYOK credential UI
- billing
- RAG
- Cursor SDK
