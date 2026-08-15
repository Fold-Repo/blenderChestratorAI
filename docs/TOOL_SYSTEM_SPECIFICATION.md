# Tool System Specification

## MVP Tools

### get_scene_summary
Permission: READ_ONLY.
Returns scene name, render engine, frame, object count, cameras, lights and collections.

### get_selected_objects
Permission: READ_ONLY.
Returns selected object identifiers and relevant transforms/properties.

### find_objects
Permission: READ_ONLY.
Searches objects using deterministic filters such as exact name, contains, type or collection.

### select_objects
Permission: SAFE_WRITE.
Selects a known set of object IDs. This is reversible and non-destructive.

### modify_object_transform
Permission: APPROVAL_REQUIRED.
Changes location/rotation/scale for a bounded set of object IDs.

## Tool Contract
Every tool must define:
- `name`
- `version`
- `description`
- JSON schema
- permission level
- target constraints
- validator
- executor
- result schema
- error codes
- timeout
- audit fields

## Example
```json
{
  "name": "modify_object_transform",
  "version": "1",
  "arguments": {
    "object_ids": ["..."],
    "location_delta": [ -2, 0, 0 ],
    "rotation_delta": [0, 0, 0],
    "scale_multiplier": [1, 1, 1]
  }
}
```

The model may propose this structure; the executor must validate IDs, types, ranges and permissions before touching Blender.

## Future Tool Families
Inspection, materials, cameras/lights, collections, modifiers, creation, deletion, rendering and asset dependencies should be added incrementally.
