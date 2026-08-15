# Next Phase — AI 3D Production Orchestrator

Development planning for work **after** the completed Blender AI Copilot MVP.

This folder is the planning home for the next product: a **local-first, testable AI 3D Production Orchestrator**. It does not replace the original MVP docs. Those remain the source of truth for what already shipped.

**Do not implement the entire roadmap in one session.** Every batch is independently testable and must STOP when complete.

```text
READ → PLAN → IMPLEMENT → TEST → MANUAL VALIDATION → DOCUMENT → STOP
```

Source roadmap: [`../MASTER_CURSOR_DEVELOPMENT_PROMPT.md`](../MASTER_CURSOR_DEVELOPMENT_PROMPT.md)

---

## 1. Starting point: completed MVP

The Copilot MVP (batches MVP-0 through MVP-9) is complete and is **Milestone A**: chat plus structured Blender operations.

### What already exists

| Area | Current MVP capability |
|---|---|
| Add-on | Native Copilot panel, chat, preferences, login, packaging zip |
| Chat | Backend-connected conversation, retry, cancel, connection status |
| Scene context | Deterministic collector for scene, objects, selection, transforms |
| Tools | Allow-listed tools: scene summary, selected objects, find, select, bounded transform |
| Safety | Dual validation, preview / approve / apply / undo; no arbitrary Python or shell |
| Agent | Provider-neutral scene agent; local rule-based provider or OpenAI Responses |
| Backend | Auth tokens, project ownership, conversations, runs, usage, audit |
| Hardening | Rate limits, 1MB JSON limit, log/audit redaction |

### What this next phase must not break

- Deterministic Blender tools instead of LLM-generated Python
- Preview → approval → execution → undo
- Project ownership and authenticated API scope
- Local-first development (no cloud required)
- One-batch-at-a-time Cursor workflow

Original MVP planning remains in `docs/` (`MVP_SCOPE.md`, `SYSTEM_ARCHITECTURE.md`, `IMPLEMENTATION_PLAN.md`, `SECURITY_BASELINE.md`).

---

## 2. Product direction

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

The AI reasons and plans. Registered tools execute.

```text
User → AI intent → Structured specification → Geometry/scene/task plan
  → Schema validation → Permission validation → Execution Manager
  → Deterministic Blender tool → Blender
```

Never build `LLM → arbitrary Blender Python → execute`.

---

## 3. Local-first execution

Initial mode is always `LOCAL`. Remote execution starts as an interface/stub.

```text
LOCAL → REMOTE (stub) → AUTO (later)
```

Do not spend on cloud infrastructure until the local product is useful end-to-end.

Recommended hardware guidance (recommendation, not a hard plugin block):

| RAM | Guidance |
|---|---|
| <16 GB | Heavy local workflows unsupported |
| 16–31 GB | Basic local workflows with limitations |
| 32 GB+ | Recommended development baseline |
| 64 GB+ | Heavy local workflows |

GPU/VRAM and Blender version also influence recommendations.

---

## 4. Phase map

```text
PHASE 0   Foundation & Execution
PHASE 1   Reference Intelligence
PHASE 2   Object Generation
PHASE 3   Object Refinement & Assets
PHASE 4   Scene & Multi-Object Generation
PHASE 5   Architecture & Environment
PHASE 6   World Generation
PHASE 7   Animation & Camera
PHASE 8   Simulation & Story
PHASE 9   Rendering & Remote Compute
PHASE 10  Video AI Orchestration
PHASE 11  Complete AI 3D Production Orchestrator
```

### Product milestones

| Milestone | Meaning | Status |
|---|---|---|
| A | Chat + structured Blender operations | **Done (Copilot MVP)** |
| B | Reference image → editable cup locally | Planned (Phase 2) |
| C | Multi-reference object generation + refinement | Planned (Phase 3) |
| D | Multi-object scenes | Planned (Phase 4) |
| E | Dimensioned house generation | Planned (Phase 5) |
| F | Complete environment/world | Planned (Phase 6) |
| G | Animation | Planned (Phase 7) |
| H | Local rendering | Planned (Phase 9) |
| I | Remote rendering | Planned (Phase 9) |
| J | Video AI integration | Planned (Phase 10) |
| K | Full AI 3D Production Orchestrator | Planned (Phase 11) |

---

## 5. Batch plan

Implement only the requested batch. Each batch ends with **STOP**.

### Phase 0 — Foundation & Execution

First work after the Copilot MVP. Makes execution a first-class, testable contract.

| Batch | Goal | Notes |
|---|---|---|
| **0.1** | Repository & architecture baseline | Plan only. Write current-state docs. No product code. |
| **0.2** | Execution Manager | `ExecutionManager`, `LocalExecutor`, `RemoteExecutor` stub, `ExecutionJob`. Prove with `CREATE_CUBE`. |
| **0.3** | Local capability detection | `LocalCapabilityProfile` + Settings → Execution UI (RAM, GPU, VRAM, CPU, Blender). |
| **0.4** | Local job lifecycle | `QUEUED → RUNNING → COMPLETED / FAILED / CANCELLED` with progress, logs, errors. |

### Phase 1 — Reference Intelligence

| Batch | Goal |
|---|---|
| 1.1 | Reference upload (PNG/JPG/JPEG/WebP), labels, persist with project |
| 1.2 | Multimodal analysis (type, parts, symmetry, dimensions, confidence). No geometry. |
| 1.3 | Versioned `ObjectSpecification` |
| 1.4 | Conversational spec editing (“Height is 120mm”) |

### Phase 2 — Object Generation

Start simple: **Cup → Bottle → Vase → Plate**.

| Batch | Goal |
|---|---|
| 2.1 | `GeometryStrategy` registry; implement CUP only |
| 2.2 | `ObjectSpecification` → validated `GeometryPlan` (no Blender execution) |
| 2.3 | Deterministic cup tools (`create_revolved_body`, handle, bevel, dimensions) |
| 2.4 | End-to-end: reference → spec → plan → preview → approval → Blender cup |
| 2.5 | Bottle strategy |
| 2.6 | Vase + plate strategies |

### Phase 3 — Object Refinement & Assets

| Batch | Goal |
|---|---|
| 3.1 | Reference comparison report (do not auto-modify) |
| 3.2 | Conversational correction with preview/approval |
| 3.3 | Object history / versioning |
| 3.4 | Asset library |

### Phase 4 — Scene & Multi-Object Generation

| Batch | Goal |
|---|---|
| 4.1 | `SceneSpecification` |
| 4.2 | Multi-object generation (table + chairs) |
| 4.3 | Spatial layout agent |
| 4.4 | Scene conversational editing |

### Phase 5 — Architecture & Environment

| Batch | Goal |
|---|---|
| 5.1 | `BuildingSpecification` from plans/elevations |
| 5.2 | Parametric building generator |
| 5.3 | House reference-to-3D |
| 5.4 | Interior generator |
| 5.5 | Exterior environment |

### Phase 6 — World Generation

| Batch | Goal |
|---|---|
| 6.1 | `WorldSpecification` |
| 6.2 | Procedural world assembly |
| 6.3 | World editing agent |

### Phase 7 — Animation & Camera

Do not start until objects/environments are reliable.

| Batch | Goal |
|---|---|
| 7.1 | Camera agent |
| 7.2 | Object animation |
| 7.3 | Character system |
| 7.4 | Timeline agent |

### Phase 8 — Simulation & Story

| Batch | Goal |
|---|---|
| 8.1 | One deterministic physics type (rigid body) |
| 8.2 | Environment effects, one at a time |
| 8.3 | Story agent |

### Phase 9 — Rendering & Remote Compute

Only after the local production workflow is already useful.

| Batch | Goal |
|---|---|
| 9.1 | Local render job |
| 9.2 | Real `RemoteExecutor` (one worker) |
| 9.3 | Cloud Blender worker |
| 9.4 | Remote render queue |
| 9.5 | Local / Remote / Auto mode |
| 9.6 | Remote preview |
| 9.7 | Render caching / scene versions |

### Phase 10 — Video AI Orchestration

| Batch | Goal |
|---|---|
| 10.1 | Replaceable `VideoProvider` |
| 10.2 | Blender-to-video workflow |
| 10.3 | `VideoGenerationJob` |
| 10.4 | Hybrid Blender + video AI production |

### Phase 11 — Complete Orchestrator

| Batch | Goal |
|---|---|
| 11.1 | Unified project understanding |
| 11.2 | Task planning agent |
| 11.3 | Multi-agent orchestration where it adds value |
| 11.4 | Full production MVP (house commercial end-to-end) |

---

## 6. Reuse vs. new work

Build on the Copilot MVP. Do not rewrite it.

**Reuse**

- Add-on UI, chat, preferences, auth token client
- Tool registry, executor, approval/preview/undo
- Scene context collector
- Scene agent loop and provider factory
- Backend projects, conversations, runs, usage, audit
- Contracts package and test/CI baseline

**Add in Phase 0**

- `ExecutionManager` / `LocalExecutor` / `RemoteExecutor` stub
- `ExecutionJob` contract shared by local and remote
- `LocalCapabilityProfile`
- Job lifecycle and progress

**Defer until a later batch explicitly asks**

- Cloud GPU/CPU farms
- BYOK, billing, teams, SSO
- RAG / project knowledge
- Cursor SDK
- Animation, worlds, video AI
- Arbitrary Python or shell execution

---

## 7. How to run a batch

When the developer says `Implement Batch X`:

1. **Read** this README, [`MASTER_CURSOR_DEVELOPMENT_PROMPT.md`](../MASTER_CURSOR_DEVELOPMENT_PROMPT.md), current-state docs in this folder, and relevant source.
2. **Analyze** reusable components, files, APIs, Blender changes, tests, and risks.
3. **Plan** before editing (batch, goal, files, APIs, tests, acceptance criteria).
4. **Implement only that batch.**
5. **Test** (unit, integration, Blender where applicable).
6. **Document** implemented vs planned vs deferred.
7. **Report** and **STOP.**

### Standard completion report

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

## 8. Living docs in this folder

After every implemented batch, update at least:

```text
docs/next phase/
├── README.md                  ← this planning index
├── CURRENT_STATE.md           ← created in Batch 0.1
├── ARCHITECTURE.md
├── IMPLEMENTATION_STATUS.md
├── TESTING.md
└── CHANGELOG.md
```

Batch 0.1 specifically creates `ORCHESTRATOR_CURRENT_STATE.md` (or `CURRENT_STATE.md`) covering capabilities, reusable components, gaps, debt, risks, and the Batch 0.2 plan.

Never document planned functionality as implemented.

---

## 9. Testing and security

Every batch needs tests matching its scope:

- Unit: schemas, validators, planners, state transitions, capability detection
- Integration: AI → schema → planner → tool → Blender; ExecutionManager → executor
- Blender: dimensions, names, counts, transforms, relationships when geometry changes
- Manual: every Blender-generating batch must be validated in real Blender

Never allow:

- unrestricted AI-generated shell or Python
- arbitrary filesystem or network access
- cross-project object access
- unapproved destructive operations

Validate tool arguments, IDs, project ownership, permissions, resource limits, file types, and job scope.

Do not silently spend money. Remote work stays optional, cancellable, and local-first until proven.

---

## 10. First implementation prompt (Batch 0.1)

Paste into Cursor when ready to start. **No product code.**

```text
Read docs/MASTER_CURSOR_DEVELOPMENT_PROMPT.md and docs/next phase/README.md completely.

We have already completed the original Blender AI Copilot MVP (Milestone A).

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

Create/update only the current-state documentation required by Batch 0.1
in docs/next phase/.

Do NOT implement execution manager, capability detection, reference upload,
image analysis, object generation, remote rendering, animation, world
generation or any future batch.

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

After Batch 0.1 is reviewed, the next prompt is **Batch 0.2 — Execution Manager** only (`CREATE_CUBE` local proof, remote stub, no cloud).

---

## 11. Absolute rules

- Never implement the entire roadmap in one Cursor session.
- Never silently skip batch boundaries.
- Never assume a feature works because code compiles.
- Every Blender-changing batch must be manually validated.
- Every future capability must build on a verified previous capability.

```text
BATCH → TEST → VALIDATE → DOCUMENT → STOP → NEXT BATCH
```
