# MASTER CURSOR DEVELOPMENT PROMPT
## Blender AI 3D Orchestrator — Local-First, Testable MVP Development Roadmap

Version: 1.0 — August 2026

## 1. Purpose

Continue development of the completed Blender AI Copilot MVP into an **AI 3D Production Orchestrator**.

Long-term capability:

```text
Reference / Text / Existing Scene
            ↓
      AI Understanding
            ↓
  Structured Specification
            ↓
     Planning / Reasoning
            ↓
     Execution Manager
       ↙            ↘
   LOCAL          REMOTE
      ↓               ↓
   Blender        Cloud GPU/CPU
       \             /
        ↓           ↓
       Editable 3D World
              ↓
      Animation / Simulation
              ↓
        Local / Remote Render
              ↓
       Optional Video AI
              ↓
        Final Production
```

The product should eventually support objects, scenes, houses, worlds, animation, simulation, rendering and video orchestration.

---

# 2. NON-NEGOTIABLE DEVELOPMENT RULE

**Never implement the entire roadmap at once.**

Every batch must be independently testable:

```text
READ → PLAN → IMPLEMENT → TEST → MANUAL VALIDATION → DOCUMENT → STOP
```

Cursor must **never automatically continue to the next batch**. The developer explicitly starts every next batch.

---

# 3. CORE ARCHITECTURAL PRINCIPLE

Do not build:

```text
LLM → arbitrary Blender Python → execute
```

Build:

```text
User
 ↓
AI intent
 ↓
Structured specification
 ↓
Geometry/scene/task plan
 ↓
Schema validation
 ↓
Permission validation
 ↓
Execution Manager
 ↓
Deterministic Blender tool
 ↓
Blender
```

The AI reasons and plans. Registered tools execute.

---

# 4. LOCAL-FIRST STRATEGY

Development must not require cloud infrastructure.

Initial mode:

```text
Execution Mode = LOCAL
```

Eventually support:

```text
LOCAL
REMOTE
AUTO
```

Remote execution must initially be an interface/stub. Do not spend on cloud infrastructure until the local product is useful end-to-end.

---

# 5. LOCAL SYSTEM CAPABILITY

Create a `LocalCapabilityProfile` containing:

- RAM and available RAM
- CPU model/cores/threads
- GPU/vendor/VRAM
- GPU compute/render support
- Blender version
- OS
- free disk space
- Cycles/Eevee availability

Recommended guidance:

```text
<16 GB       Heavy local workflows unsupported
16–31 GB     Basic/local workflows with limitations
32 GB+       Recommended development baseline
64 GB+       Heavy local workflows
```

32 GB should be a recommendation, not a hard block on opening the plugin. GPU capability must also influence recommendations.

---

# 6. EXECUTION ABSTRACTION

Create:

```text
ExecutionManager
 ├── LocalExecutor
 └── RemoteExecutor (interface/stub initially)
```

Every workload should use a common `ExecutionJob` contract.

Example:

```json
{
  "job_id": "...",
  "project_id": "...",
  "scene_version": "...",
  "type": "MODEL_GENERATION",
  "execution_mode": "LOCAL",
  "requirements": {
    "ram_gb": 16,
    "gpu_vram_gb": 8
  },
  "priority": "normal",
  "status": "queued"
}
```

Local and remote must consume the same job contract.

---

# 7. MASTER PHASE MAP

```text
PHASE 0  Foundation & Execution
PHASE 1  Reference Intelligence
PHASE 2  Object Generation
PHASE 3  Object Refinement & Assets
PHASE 4  Scene & Multi-Object Generation
PHASE 5  Architecture & Environment
PHASE 6  World Generation
PHASE 7  Animation & Camera
PHASE 8  Simulation & Story
PHASE 9  Rendering & Remote Compute
PHASE 10 Video AI Orchestration
PHASE 11 Complete AI 3D Production Orchestrator
```

---

# PHASE 0 — FOUNDATION & EXECUTION

## BATCH 0.1 — Repository & Architecture Baseline

**Plan only. No product implementation.**

Inspect the existing MVP:

- repository structure
- architecture documents
- agent
- Blender tool system
- chat UI
- project/scene state
- backend/API
- database
- tests
- security
- current local execution

Create/update:

`docs/ORCHESTRATOR_CURRENT_STATE.md`

Document:

- current capabilities
- reusable components
- gaps
- technical debt
- risks
- integration points
- files that should not be changed
- recommended Batch 0.2 plan

**STOP.**

## BATCH 0.2 — Execution Manager

Implement:

- `ExecutionManager`
- `LocalExecutor`
- `RemoteExecutor` interface/stub
- `ExecutionJob`
- `ExecutionResult`
- `ExecutionStatus`

Use a deterministic test job such as `CREATE_CUBE` to prove local execution.

No cloud infrastructure.

**STOP.**

## BATCH 0.3 — Local System Capability Detection

Implement `LocalCapabilityProfile` and Settings → Execution UI.

Show RAM, GPU, VRAM, CPU, Blender version and capability rating.

**STOP.**

## BATCH 0.4 — Local Job Lifecycle

Support:

```text
QUEUED → RUNNING → COMPLETED
                 ↘ FAILED
                 ↘ CANCELLED
```

Add progress, logs, timestamps, errors and result references.

**STOP.**

---

# PHASE 1 — REFERENCE INTELLIGENCE

## BATCH 1.1 — Reference Upload

Support PNG/JPG/JPEG/WebP.

Allow upload, remove, replace, optional labels and multiple references.

Labels:

- front/back/left/right/top/bottom
- perspective
- technical drawing
- sketch
- unknown

Persist references with the project.

**STOP.**

## BATCH 1.2 — Multimodal Reference Analysis

Analyze:

- object type
- components
- geometry
- symmetry
- dimensions
- annotations
- material appearance
- unknowns
- confidence

No Blender geometry yet.

Use the existing provider abstraction.

**STOP.**

## BATCH 1.3 — Object Specification

Create a versioned `ObjectSpecification` containing:

- object type
- units
- dimensions
- components
- relationships
- constraints
- sources
- confidence
- unknowns

Dimension sources:

```text
USER_CONFIRMED
DIMENSION_DRAWING
MULTI_VIEW_INFERENCE
SINGLE_VIEW_INFERENCE
AI_ESTIMATE
UNKNOWN
```

**STOP.**

## BATCH 1.4 — Conversational Specification Editing

Allow users to say:

> Height is 120mm.

> Wall thickness is 4mm.

> Handle is 8mm.

Update the specification rather than creating conflicting values.

**STOP.**

---

# PHASE 2 — OBJECT GENERATION

Start with simple objects:

```text
Cup → Bottle → Vase → Plate
```

## BATCH 2.1 — Geometry Strategy Registry

Create a `GeometryStrategy` abstraction.

Eventually support cup, bottle, vase, plate, table, chair, cabinet, lamp, mechanical and architectural strategies.

Initially implement only CUP.

Cup strategy:

```text
Profile → Revolve → Wall Thickness → Handle → Bevel
```

**STOP.**

## BATCH 2.2 — Geometry Plan

Convert `ObjectSpecification` into validated `GeometryPlan`.

Example:

```json
{
  "strategy": "CUP",
  "operations": [
    {"operation": "CREATE_REVOLVED_BODY", "height": 120, "radius": 45, "wall_thickness": 4},
    {"operation": "CREATE_HANDLE", "diameter": 8, "offset": 8}
  ]
}
```

No Blender execution yet.

**STOP.**

## BATCH 2.3 — Deterministic Blender Cup Generator

Implement validated Blender tools such as:

- `create_revolved_body`
- `create_curve_handle`
- `apply_bevel`
- `set_dimensions`
- `position_component`

No arbitrary AI Python.

**STOP.**

## BATCH 2.4 — Cup Reference-to-3D End-to-End MVP

Connect:

```text
Reference → Analysis → Specification → Strategy → Geometry Plan → Preview → Approval → Blender
```

The user must be able to generate an editable cup locally.

**STOP.**

## BATCH 2.5 — Bottle Generator

Add bottle strategy and deterministic tools.

**STOP.**

## BATCH 2.6 — Vase + Plate Generator

Add both strategies and tests.

**STOP.**

---

# PHASE 3 — OBJECT REFINEMENT & ASSETS

## BATCH 3.1 — Reference Comparison

Compare generated model against references for:

- silhouette
- proportions
- component position
- dimensions
- major curvature

Return a structured difference report. Do not automatically modify.

**STOP.**

## BATCH 3.2 — Conversational Object Correction

Support requests such as:

> Move the handle closer.

> Make the body wider.

> Make the rim thinner.

> Keep height exactly 120mm.

Workflow:

```text
Request → Correction Plan → Validation → Preview → Approval → Tool
```

**STOP.**

## BATCH 3.3 — Object History / Versioning

Track specification, geometry-plan and accepted correction versions. Integrate with existing undo/recovery.

**STOP.**

## BATCH 3.4 — Asset Library

Persist reusable objects/materials and allow the AI to reference them in future scenes.

**STOP.**

---

# PHASE 4 — SCENE & MULTI-OBJECT GENERATION

## BATCH 4.1 — Scene Specification

Create `SceneSpecification` for spaces, objects, quantities, relationships, positions, scale and constraints.

**STOP.**

## BATCH 4.2 — Multi-Object Generation

Example:

> Create a dining table with six matching chairs.

Generate structured, editable objects.

**STOP.**

## BATCH 4.3 — Spatial Layout Agent

Support spacing, collision avoidance, boundaries, alignment, orientation and walkways.

**STOP.**

## BATCH 4.4 — Scene Conversational Editing

Examples:

> Move all chairs closer.

> Make the table 20% larger.

> Rotate the dining set 90 degrees.

> Replace all chairs with this asset.

**STOP.**

---

# PHASE 5 — ARCHITECTURE & ENVIRONMENT

## BATCH 5.1 — Architectural Specification

Support floor plans, elevations, sections, dimensions and room relationships. Create `BuildingSpecification`.

**STOP.**

## BATCH 5.2 — Parametric Building Generator

Generate:

- foundations
- walls
- floors
- ceilings
- doors
- windows
- stairs
- roof

**STOP.**

## BATCH 5.3 — House Reference-to-3D

Inputs may include:

- front/rear/side elevations
- floor plan
- roof plan
- dimensions
- photographs

Output an editable house locally.

**STOP.**

## BATCH 5.4 — Interior Generator

Generate rooms, furniture, lighting, materials and fixtures.

**STOP.**

## BATCH 5.5 — Exterior Environment

Generate terrain, roads, vegetation, fences, driveways and exterior props.

**STOP.**

---

# PHASE 6 — WORLD GENERATION

## BATCH 6.1 — World Specification

Represent:

```text
World
 ├── Terrain
 ├── Buildings
 ├── Roads
 ├── Vegetation
 ├── Props
 ├── Characters
 ├── Lighting
 └── Weather
```

**STOP.**

## BATCH 6.2 — Procedural World Assembly

Generate a small coherent world from structured requirements.

**STOP.**

## BATCH 6.3 — World Editing Agent

Examples:

> Add 20 trees.

> Move the road east.

> Add three houses.

> Create a market.

> Make the terrain mountainous.

**STOP.**

---

# PHASE 7 — ANIMATION & CAMERA

Do not begin until objects/environments are reliable.

## BATCH 7.1 — Camera Agent

Support camera position, target, lens, depth of field and movement.

**STOP.**

## BATCH 7.2 — Object Animation

Support transforms, keyframes, paths and timing.

Example:

> Make the car drive into the driveway.

**STOP.**

## BATCH 7.3 — Character System

Introduce character assets, rigs, animation clips and paths.

**STOP.**

## BATCH 7.4 — Timeline Agent

Turn narrative into an editable timeline.

Example:

```text
0s camera starts
7s car arrives
12s car stops
15s person exits
22s person walks
28s door opens
30s shot ends
```

**STOP.**

---

# PHASE 8 — SIMULATION & STORY

## BATCH 8.1 — Physics

Start with one deterministic simulation type such as rigid body.

**STOP.**

## BATCH 8.2 — Environment Effects

Add one at a time: smoke, fire, water, weather, etc.

**STOP.**

## BATCH 8.3 — Story Agent

Convert narrative into characters, actions, timeline, camera and environment changes.

**STOP.**

---

# PHASE 9 — LOCAL RENDERING & REMOTE COMPUTE

Only after the local production workflow is already useful.

## BATCH 9.1 — Local Render Job

Support stills and animation with engine, resolution, samples and frame range.

**STOP.**

## BATCH 9.2 — Remote Executor

Implement actual `RemoteExecutor`, initially with one remote worker. Do not build a huge farm.

**STOP.**

## BATCH 9.3 — Cloud Blender Worker

Worker:

```text
receive job → obtain scene/assets → Blender headless → render → upload → report → cleanup
```

**STOP.**

## BATCH 9.4 — Remote Render Queue

Add queue, worker status, retries, progress, logs, cancellation and priority.

**STOP.**

## BATCH 9.5 — Local / Remote / Auto

Settings:

```text
○ Local
○ Remote
○ Auto
```

Auto should consider job requirements, local capability, user preference, estimated runtime, configured availability and estimated cost.

Default development mode remains LOCAL.

**STOP.**

## BATCH 9.6 — Remote Preview

Use remote rendering for complex previews while preserving local viewport interaction.

**STOP.**

## BATCH 9.7 — Render Caching / Scene Versions

Track scene, asset, material, camera, lighting and animation versions. Reuse safe unchanged outputs where possible.

**STOP.**

---

# PHASE 10 — VIDEO AI ORCHESTRATION

## BATCH 10.1 — Video Provider Abstraction

Create a replaceable `VideoProvider` interface.

**STOP.**

## BATCH 10.2 — Blender-to-Video Workflow

```text
3D Scene → Controlled Blender Render → Reference Frames/Video → Video AI → Output
```

**STOP.**

## BATCH 10.3 — Video Production Job

Create `VideoGenerationJob` with source scene, frames, prompt, duration, aspect ratio, resolution, provider and status.

**STOP.**

## BATCH 10.4 — Hybrid Production

Allow Blender to provide deterministic geometry/camera and video AI to provide cinematic/generative enhancement.

**STOP.**

---

# PHASE 11 — COMPLETE AI 3D PRODUCTION ORCHESTRATOR

## BATCH 11.1 — Unified Project Understanding

Agent understands references, objects, assets, scenes, worlds, animation, render jobs, video jobs and project history.

**STOP.**

## BATCH 11.2 — Task Planning Agent

Example request:

> Create a 30-second cinematic commercial for this house.

Visible plan:

```text
1. Analyze references
2. Build house
3. Build environment
4. Add furniture
5. Create camera
6. Create lighting
7. Create animation
8. Render
9. Optional video AI
10. Assemble output
```

**STOP.**

## BATCH 11.3 — Multi-Agent Orchestration

Only create specialized agents where they provide measurable value.

Potential agents:

- Supervisor
- Reference
- Asset
- Scene
- Architecture
- Animation
- Camera
- Render
- Video
- QA

**STOP.**

## BATCH 11.4 — Full Production MVP

End-to-end local-first workflow:

```text
House references
 ↓
Reference analysis
 ↓
Missing-information questions
 ↓
Confirmed specification
 ↓
House generation
 ↓
Interior/environment
 ↓
Car + character
 ↓
Camera
 ↓
Animation
 ↓
Local/remote render choice
 ↓
Render
 ↓
Optional video AI
 ↓
Final video
 ↓
Conversational revision
```

This is the first true **AI 3D Production Orchestrator MVP**.

**STOP.**

---

# 9. TESTING RULES

Every batch must include tests appropriate to its scope.

### Unit tests

Schemas, validators, planners, state transitions, capability detection and unit conversion.

### Integration tests

AI → schema → planner → tool → Blender and ExecutionManager → executor.

### Blender tests

Verify dimensions, names, counts, transforms, relationships, materials, animation and render settings as applicable.

### Manual validation

Every Blender-generating batch requires an actual Blender validation step.

Record:

- input
- expected result
- actual result
- limitations

---

# 10. SECURITY RULES

Never allow:

- unrestricted AI-generated shell commands
- unrestricted AI-generated Python execution
- arbitrary filesystem access
- arbitrary network access
- cross-project object access
- unapproved destructive operations

Validate tool arguments, IDs, project ownership, permissions, resource limits, file types and job scope.

---

# 11. COST CONTROL

Cloud infrastructure is optional until the local product is proven.

Before remote execution becomes generally available:

- show estimated cost where possible
- allow local-only mode
- allow remote-disabled mode
- support cancellation
- prevent duplicate jobs
- cache safe outputs
- use low-quality previews before final renders

Do not silently spend money.

---

# 12. DOCUMENTATION

After every batch update the appropriate documentation, at minimum:

```text
docs/
├── CURRENT_STATE.md
├── ARCHITECTURE.md
├── IMPLEMENTATION_STATUS.md
├── TESTING.md
└── CHANGELOG.md
```

Clearly distinguish:

- implemented
- planned
- experimental
- mocked
- deferred

Never document planned functionality as implemented.

---

# 13. STANDARD CURSOR WORKFLOW

Whenever the developer says `Implement Batch X`:

### Step 1 — Read

Read this master prompt, current architecture, implementation status, previous batch documentation and relevant source code.

### Step 2 — Analyze

Identify reusable components, affected files, dependencies, risks, migrations, APIs, Blender changes and tests.

### Step 3 — Plan

Before editing, provide:

```text
Batch
Goal
Files to change
Files to create
Database changes
API changes
Blender changes
AI changes
Tests
Risks
Acceptance criteria
```

### Step 4 — Implement

Implement ONLY the requested batch.

### Step 5 — Test

Run appropriate tests, lint, type checks, Blender tests and manual validation instructions.

### Step 6 — Document

Update implementation documentation.

### Step 7 — Report

Use:

```text
STATUS: COMPLETE / BLOCKED
BATCH: X.X
IMPLEMENTED: ...
FILES CHANGED: ...
API: ...
DATABASE: ...
BLENDER: ...
AI: ...
TESTS: ...
MANUAL VALIDATION: ...
KNOWN LIMITATIONS: ...
DEFERRED: ...
NEXT BATCH: ...

STOP
```

---

# 14. FIRST CURSOR PROMPT

Paste this into Cursor after adding this file:

```text
Read MASTER_CURSOR_DEVELOPMENT_PROMPT.md completely.

We have already completed the original Blender AI Copilot MVP.

Do NOT implement anything yet.

Perform Batch 0.1 — Repository & Architecture Baseline only.

Inspect the repository and existing architecture/documentation.

Determine:
1. Current MVP capabilities.
2. Reusable components.
3. Current agent architecture.
4. Current Blender tool architecture.
5. Current chat architecture.
6. Current project/scene state model.
7. Current API/backend architecture.
8. Current database structure.
9. Current local execution capabilities.
10. Existing tests.
11. Existing security boundaries.
12. Technical debt.
13. Gaps for the AI 3D Orchestrator.
14. What should change.
15. What should NOT change.
16. Dependencies and risks.
17. Proposed Batch 0.2 implementation plan.

Create/update only the current-state documentation required by Batch 0.1.

Do NOT implement execution manager, capability detection, reference upload, image analysis, object generation, remote rendering, animation, world generation or any future batch.

At the end provide:
STATUS
CURRENT MVP CAPABILITIES
REUSABLE COMPONENTS
ARCHITECTURAL GAPS
RISKS
PROPOSED BATCH 0.2 PLAN
FILES AFFECTED
TESTING PLAN

STOP.
```

---

# 15. SECOND CURSOR PROMPT — AFTER BATCH 0.1 REVIEW

```text
Implement Batch 0.2 — Execution Manager.

Read MASTER_CURSOR_DEVELOPMENT_PROMPT.md and the Batch 0.1 documentation first.

Implement ONLY Batch 0.2.

Create the execution abstraction:
- ExecutionManager
- LocalExecutor
- RemoteExecutor interface/stub
- ExecutionJob
- ExecutionResult
- ExecutionStatus

Local execution must work.
Remote infrastructure must NOT be required.

Use a deterministic test job such as CREATE_CUBE to prove the abstraction.

Do not implement capability detection, reference upload, image analysis, object specification, object generation, cloud infrastructure, animation or world generation.

Run tests, update documentation and provide the standard completion report.

STOP after Batch 0.2.
```

---

# 16. PRODUCT MILESTONES

```text
MILESTONE A — Chat + structured Blender operations
MILESTONE B — Reference image → editable cup locally
MILESTONE C — Multi-reference object generation + refinement
MILESTONE D — Multi-object scenes
MILESTONE E — Dimensioned house generation
MILESTONE F — Complete environment/world
MILESTONE G — Animation
MILESTONE H — Local rendering
MILESTONE I — Remote rendering
MILESTONE J — Video AI integration
MILESTONE K — Full AI 3D Production Orchestrator
```

---

# 17. FINAL PRODUCT DEFINITION

The product should feel like:

> **Tell the AI what you want to create. It understands your references and intent, builds an editable 3D world, lets you refine it through conversation, handles animation and rendering, and uses the best available AI models where they add value.**

The core product is the orchestration layer, not a single model.

The system must remain independent of:

- one LLM
- one vision model
- one 3D generator
- one video model
- one GPU provider
- one execution environment

Blender is the first and primary editable 3D execution environment.

Local execution is the initial development environment.

Remote compute is an optional acceleration layer.

External AI models are interchangeable workers.

---

# 18. ABSOLUTE RULE

Never implement the entire roadmap in one Cursor session.

Never silently skip batch boundaries.

Never assume a feature works because code compiles.

Every batch must produce a testable unit.

Every Blender-changing batch must be manually validated.

Every future capability must build on a verified previous capability.

```text
BATCH
 ↓
TEST
 ↓
VALIDATE
 ↓
DOCUMENT
 ↓
STOP
 ↓
NEXT BATCH
```

This rule takes priority over convenience.
