# Product Requirements

## Goals
- Make Blender interaction conversational.
- Ground answers in live scene data.
- Make modifications predictable and reviewable.
- Provide a path from scene assistance to Blender development.
- Support multiple model providers.
- Support managed AI and BYOK.

## Personas
### 1. Blender Artist
Needs scene inspection, repetitive operations, optimisation and creative assistance.

### 2. Technical Artist
Needs automation, procedural workflows, standards checking and debugging.

### 3. Blender Developer
Needs project-aware coding assistance and agentic development.

### 4. Studio/Team
Needs shared project knowledge, standards and usage controls.

## Functional Requirements
FR-01 Embedded chat.
FR-02 Current selection awareness.
FR-03 Structured scene context.
FR-04 Read-only scene tools.
FR-05 Safe write tools.
FR-06 Approval-required write actions.
FR-07 Action preview.
FR-08 Undo/recovery.
FR-09 Streaming.
FR-10 Provider selection.
FR-11 Usage accounting.
FR-12 Project isolation.
FR-13 Audit trail.
FR-14 Future RAG.
FR-15 Future coding-agent orchestration.

## Non-Functional Requirements
- Secure by default.
- Provider-independent.
- Observable.
- Idempotent where possible.
- Recoverable.
- Low latency for local read operations.
- Explicit permission boundaries.
- Versioned tool schemas.
- Backward-compatible API contracts.

## Acceptance Principle
Every user-visible modification must be explainable as a structured action with target, parameters, risk class and execution result.
