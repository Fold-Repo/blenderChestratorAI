# Blender AI Copilot — MVP Implementation Prompt Pack

## Purpose

This document is the execution companion to the Blender AI Copilot development plan.

The development plan defines the architecture and sequence. This file defines the **Cursor execution prompts for each MVP batch**.

Cursor must treat the existing planning documents in the repository as the architectural source of truth and this document as the implementation sequence.

---

# MASTER RULE FOR ALL MVP BATCHES

Before implementing any MVP batch, Cursor MUST:

1. Read `PROJECT_DOCUMENT.md`.
2. Read `SYSTEM_ARCHITECTURE.md`.
3. Read `IMPLEMENTATION_PLAN.md`.
4. Read `MVP_SCOPE.md`.
5. Read `DEVELOPMENT_RULES.md`.
6. Read the relevant architecture document(s) for the current batch.
7. Inspect the current repository and existing implementation.
8. Determine what has already been completed.
9. Identify contradictions or blockers.
10. Produce a short implementation plan for the current batch.
11. Implement ONLY the current batch.
12. Run appropriate tests and validation.
13. Update documentation.
14. Report completion and known limitations.
15. STOP.

## Critical Scope Rule

Never implement future MVP batches automatically.

If a future dependency is needed, create only the smallest interface/stub required for the current batch.

Do NOT jump ahead into:

- RAG
- BYOK
- Cursor SDK
- coding agents
- billing
- subscriptions
- teams
- enterprise
- arbitrary Python execution
- shell execution
- multi-application support

unless the current MVP explicitly requires it.

---

# MVP BATCH MAP

| Batch | Objective | Main Result |
|---|---|---|
| MVP-0 | Project Foundation | Development-ready repository |
| MVP-1 | Blender Add-on Shell | Copilot exists inside Blender |
| MVP-2 | Chat UI | Interactive native chat |
| MVP-3 | Backend Connection | Blender ↔ backend communication |
| MVP-4 | Scene Context Engine | Structured Blender context |
| MVP-5 | Tool System | Deterministic Blender tools |
| MVP-6 | AI Scene Agent | Natural language → tools |
| MVP-7 | Safe Modification | Structured modification proposals |
| MVP-8 | Preview/Approval/Undo | Safe end-to-end modification |
| MVP-9 | Production Hardening | Beta-ready MVP |

---

# MVP-0 — PROJECT FOUNDATION

## Objective

Create the development foundation.

Do NOT build AI functionality.

Do NOT build scene intelligence.

Do NOT implement provider integrations.

Do NOT implement RAG.

Do NOT implement Cursor SDK.

Do NOT implement BYOK.

Do NOT implement billing.

## Read

- `PROJECT_DOCUMENT.md`
- `SYSTEM_ARCHITECTURE.md`
- `IMPLEMENTATION_PLAN.md`
- `MVP_SCOPE.md`
- `DEVELOPMENT_RULES.md`
- `BLENDER_ADDON_ARCHITECTURE.md`
- `RESEARCH_AND_DECISIONS.md`

## Implement

Create:

- monorepo structure
- Blender add-on package
- backend package
- shared contracts package
- development configuration
- logging abstraction
- error abstraction
- backend `/health`
- basic CI
- test foundation
- developer documentation
- `.env.example`

Create a minimal native Blender AI Copilot panel shell, but no real chat functionality.

## Completion Criteria

- repository builds
- backend starts
- `/health` works
- Blender add-on registers/unregisters
- Blender panel renders
- tests run
- lint/type checks run
- CI is configured
- no secrets committed
- no AI provider integrated

## Stop Condition

After validation, STOP.

Do not start MVP-1.

---

# MVP-1 — BLENDER ADD-ON SHELL

## Objective

Turn the existing Blender add-on foundation into a clean, usable product shell.

The only goal is:

> Install Blender AI Copilot → enable it → open the Copilot workspace.

## Read

- `BLENDER_ADDON_ARCHITECTURE.md`
- `CHAT_UI_SPECIFICATION.md`
- `PROJECT_DOCUMENT.md`
- `MVP_SCOPE.md`

## Implement

Build:

- native Blender workspace/panel
- Copilot header
- status indicator
- empty conversation state
- composer shell
- settings entry point
- add-on state management
- UI registration lifecycle
- clean separation between UI/state/configuration

The UI should look intentional and product-quality even though it does not communicate with the backend yet.

## Do NOT implement

- AI
- backend communication
- provider APIs
- scene tools
- scene context
- RAG
- authentication

## Completion Criteria

A developer can:

1. Install the add-on.
2. Enable it.
3. Open the Copilot workspace.
4. See the Copilot UI.
5. Disable/re-enable the add-on without errors.

## Stop Condition

Test it in Blender.

Report results.

STOP.

---

# MVP-2 — CHAT UI

## Objective

Make the Blender chat interface interactive using local/mock state.

There is still NO AI.

## Read

- `CHAT_UI_SPECIFICATION.md`
- `BLENDER_ADDON_ARCHITECTURE.md`
- `MVP_SCOPE.md`

## Implement

Add:

- conversation state
- user messages
- assistant messages
- message timestamps/state where appropriate
- composer input
- send action
- loading state
- error state
- retry
- clear conversation
- cancellation state
- tool activity placeholder
- action proposal placeholder

Use a local/mock response layer.

Example:

User:

> Hello

Mock assistant:

> Blender AI Copilot is ready.

## Do NOT implement

- real AI
- provider APIs
- backend networking
- scene tools
- RAG
- authentication

## Completion Criteria

The user can have a complete mock conversation inside Blender.

## Stop Condition

Test UI interactions and state transitions.

STOP.

---

# MVP-3 — BACKEND CONNECTION

## Objective

Connect the Blender add-on to the backend.

## Read

- `API_SPECIFICATION.md`
- `SYSTEM_ARCHITECTURE.md`
- `BLENDER_ADDON_ARCHITECTURE.md`
- `CHAT_UI_SPECIFICATION.md`

## Implement

Backend:

- API versioning foundation
- project/conversation API foundation
- request IDs
- structured API errors
- basic conversation creation
- basic run creation

Add-on:

- API client
- connection configuration
- request handling
- response parsing
- timeout handling
- retry strategy where appropriate
- connection status

The first real interaction may simply return a backend-generated response.

## Target Flow

```text
Blender UI
    ↓
API Client
    ↓
Backend
    ↓
Structured Response
    ↓
Blender UI
```

## Do NOT implement

- AI provider
- agent
- scene tools
- RAG
- BYOK
- Cursor SDK
- billing

## Completion Criteria

A message can travel:

```text
Blender → Backend → Blender
```

reliably.

## Stop Condition

Test network failures, invalid responses and backend unavailable scenarios.

STOP.

---

# MVP-4 — SCENE CONTEXT ENGINE

## Objective

Make the system understand Blender's current scene through deterministic code.

## Read

- `BLENDER_ADDON_ARCHITECTURE.md`
- `TOOL_SYSTEM_SPECIFICATION.md`
- `SYSTEM_ARCHITECTURE.md`
- `MVP_SCOPE.md`

## Implement

Create a Context Collector.

Initial context:

### Scene

- scene name
- active scene
- frame
- render engine
- object count
- camera count
- light count
- collections

### Objects

Where relevant:

- stable object identifier
- name
- type
- location
- rotation
- scale
- collection
- materials
- modifiers
- mesh statistics

### Selection

- selected object IDs
- selected object names
- types
- transforms

## Important

The context collector must use Blender's API deterministically.

Do NOT generate Python with an LLM to inspect the scene.

## Context Principle

Send the minimum context required for a request.

Do not send the entire `.blend` project by default.

## Completion Criteria

The add-on can generate accurate structured scene context.

Test:

- empty scene
- normal scene
- selected objects
- multiple collections
- cameras
- lights
- different object types

## Stop Condition

Validate the returned context against Blender manually.

STOP.

---

# MVP-5 — TOOL SYSTEM

## Objective

Build the deterministic Blender tool architecture.

## Read

- `TOOL_SYSTEM_SPECIFICATION.md`
- `SECURITY_PLAN.md`
- `BLENDER_ADDON_ARCHITECTURE.md`
- `AGENT_ARCHITECTURE.md`

## Implement

Create the tool registry and executor architecture.

Every tool must have:

- name
- version
- description
- input schema
- permission level
- validator
- executor
- result schema
- error handling
- audit metadata

## MVP Tools

Implement:

1. `get_scene_summary`
2. `get_selected_objects`
3. `find_objects`
4. `select_objects`

Prepare the architecture for:

5. `modify_object_transform`

but do not make modification execution part of the current batch unless required by tests.

## Permission Classes

Implement:

### READ_ONLY

- get_scene_summary
- get_selected_objects
- find_objects

### SAFE_WRITE

- select_objects

Future modification tools must use:

### APPROVAL_REQUIRED

## Security

Never trust tool arguments.

Validate:

- types
- object IDs
- allowed values
- project/scene scope
- permission level

## Completion Criteria

Tools can be invoked deterministically without AI.

Example:

```text
find_objects("Tree")
→ 14 objects
```

Then:

```text
select_objects([...])
→ 14 selected
```

## Stop Condition

Test every tool independently.

Test invalid arguments.

STOP.

---

# MVP-6 — AI SCENE AGENT

## Objective

Introduce the first real AI.

Use ONE provider initially.

The provider must be behind the provider abstraction.

## Read

- `AGENT_ARCHITECTURE.md`
- `AI_PROVIDER_ARCHITECTURE.md`
- `TOOL_SYSTEM_SPECIFICATION.md`
- `API_SPECIFICATION.md`
- `SECURITY_PLAN.md`

## Implement

Create:

- provider interface
- one provider adapter
- Scene Agent
- structured tool-calling loop
- tool result handling
- conversation state
- basic agent run state
- model output validation
- tool-call limits
- cancellation/error handling

## Target Flow

```text
User
 ↓
Backend
 ↓
Scene Agent
 ↓
AI Provider
 ↓
Structured Tool Call
 ↓
Blender Tool
 ↓
Tool Result
 ↓
Scene Agent
 ↓
Assistant Response
```

## Example

User:

> How many objects are in this scene?

Agent:

```text
get_scene_summary()
```

Tool:

```json
{
  "object_count": 42
}
```

Assistant:

> There are 42 objects in the current scene.

## Security

The AI must NEVER directly execute arbitrary Blender Python.

The AI may only request registered tools.

## Do NOT implement

- multiple providers
- BYOK
- Cursor SDK
- RAG
- coding agents
- billing

## Completion Criteria

Natural language requests can trigger the correct read-only tools.

Test:

- object count
- selected objects
- find objects
- nonexistent objects
- ambiguous requests
- invalid tool arguments
- provider failure

## Stop Condition

STOP after the scene-agent loop is reliable.

---

# MVP-7 — SAFE MODIFICATION

## Objective

Allow the AI to propose a Blender modification without immediately executing it.

## Read

- `TOOL_SYSTEM_SPECIFICATION.md`
- `SECURITY_PLAN.md`
- `AGENT_ARCHITECTURE.md`
- `CHAT_UI_SPECIFICATION.md`

## Implement

Add:

`modify_object_transform`

Support bounded:

- location delta
- rotation delta
- scale multiplier

The tool must require approval.

## Flow

```text
User Request
 ↓
AI
 ↓
Find Objects
 ↓
Action Proposal
 ↓
Validation
 ↓
Waiting For Approval
```

Example:

User:

> Move all trees 2 metres left.

AI:

> I found 14 tree objects.

Proposal:

```text
14 objects
X: -2m
Rotation: unchanged
Scale: unchanged
Risk: approval required
```

Do NOT execute until approval.

## Completion Criteria

The AI can produce a valid structured modification proposal.

No unapproved modification reaches Blender execution.

## Stop Condition

Test approval-required policy thoroughly.

STOP.

---

# MVP-8 — PREVIEW + APPROVAL + UNDO

## Objective

Complete the core safe modification loop.

## Read

- `CHAT_UI_SPECIFICATION.md`
- `TOOL_SYSTEM_SPECIFICATION.md`
- `SECURITY_PLAN.md`
- `BLENDER_ADDON_ARCHITECTURE.md`

## Implement

Add:

- proposal card
- target summary
- parameter summary
- Preview
- Apply
- Cancel
- execution state
- execution result
- error state
- undo support
- action history where appropriate

## Required Flow

```text
User
 ↓
AI
 ↓
Tool Calls
 ↓
Action Proposal
 ↓
Validation
 ↓
Preview
 ↓
User Approval
 ↓
Execution
 ↓
Result
 ↓
Undo
```

## Required Demo

```text
Find all objects named Tree.

Select them.

Move them 2 metres to the left.

Preview.

Apply.

Undo.
```

This is the primary MVP acceptance scenario.

## Security

Ensure:

- no approval = no execution
- stale proposals cannot execute against an incompatible scene state
- object IDs are revalidated before execution
- invalid transforms are rejected
- destructive operations remain blocked

## Completion Criteria

The entire end-to-end workflow works reliably.

## Stop Condition

STOP.

Do not begin RAG, BYOK or coding-agent integration.

---

# MVP-9 — PRODUCTION HARDENING

## Objective

Turn the functional MVP into a controlled beta candidate.

## Read

- `SECURITY_PLAN.md`
- `TESTING_STRATEGY.md`
- `DATABASE_PLAN.md`
- `API_SPECIFICATION.md`
- `BILLING_AND_SUBSCRIPTION_PLAN.md`

## Implement

### Authentication

- user authentication
- secure sessions/tokens
- project ownership

### Usage

Track:

- AI runs
- provider
- model
- token usage where available
- tool calls
- estimated cost
- project
- user

### Audit

Record:

- user
- project
- action
- tool
- parameters metadata
- approval
- execution result
- timestamp

Never store secrets in audit logs.

### Security

Test:

- prompt injection
- malformed tool calls
- unauthorized project access
- replay
- oversized requests
- credential leakage
- malicious project content
- destructive operation protection
- rate limits
- provider failures

### Packaging

Create:

- development install process
- test build
- release build process
- Blender add-on package

### Documentation

Update:

- setup
- architecture
- security
- troubleshooting
- supported Blender version
- supported AI provider
- limitations

## Completion Criteria

The system is suitable for controlled internal/beta testing.

## Stop Condition

STOP.

Report MVP v1 readiness.

---

# POST-MVP ROADMAP

Do NOT implement these as part of MVP.

They are future phases:

## Post-MVP 1 — Multiple AI Providers

- OpenAI
- Anthropic
- Gemini
- capability negotiation
- provider/model selection

## Post-MVP 2 — BYOK

- provider credential management
- encryption
- validation
- credential rotation
- user/provider scopes

## Post-MVP 3 — Project Knowledge / RAG

- document ingestion
- Blender documentation
- project files
- company standards
- embeddings
- retrieval
- citations/grounding

## Post-MVP 4 — Coding Agent Architecture

- coding-agent interface
- workspace isolation
- patch model
- tests
- code review

## Post-MVP 5 — Cursor SDK

- Cursor adapter
- local/cloud runtime
- custom tools
- workspace isolation
- commercial/legal verification

## Post-MVP 6 — Background Jobs

- Redis
- BullMQ
- project indexing
- long-running analysis
- progress events

## Post-MVP 7 — Billing

- managed AI plans
- BYOK plans
- usage metering
- subscription management
- cost controls

## Post-MVP 8 — Teams

- organizations
- memberships
- company standards
- shared projects
- usage controls

## Post-MVP 9 — Enterprise

- SSO
- private deployment
- advanced audit
- enterprise policies
- support

---

# UNIVERSAL CURSOR COMPLETION REPORT

At the end of EVERY MVP batch, return:

## 1. Status

`COMPLETE` or `BLOCKED`

## 2. Scope Implemented

List exactly what was implemented.

## 3. Files Changed

List important files.

## 4. Architecture Decisions

List decisions made and why.

## 5. Tests

List every test command executed and result.

## 6. Manual Validation

List what was manually validated.

## 7. Security Review

List security considerations for this batch.

## 8. Known Limitations

List known limitations.

## 9. Deferred Work

Explicitly list work intentionally NOT implemented because it belongs to future MVP batches.

## 10. Next MVP

State only the next MVP batch.

## 11. STOP

Do not implement the next batch automatically.

---

# FINAL PRODUCT PRINCIPLE

The system must evolve in this direction:

```text
Natural Language
       ↓
AI Reasoning
       ↓
Structured Tool
       ↓
Validation
       ↓
Permission
       ↓
Preview
       ↓
User Approval
       ↓
Deterministic Blender Execution
       ↓
Result
       ↓
Undo / Recovery
```

Never replace this architecture with:

```text
Natural Language
       ↓
LLM-generated Python
       ↓
Execute Python
```

The purpose of the MVP sequence is to prove each layer independently before adding the next layer.
