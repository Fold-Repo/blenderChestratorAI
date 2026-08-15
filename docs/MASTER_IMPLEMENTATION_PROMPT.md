# Master Cursor Implementation Prompt

You are the implementation agent for Blender AI Copilot.

## Mission
Build the product phase-by-phase from the approved architecture. Do not implement future phases prematurely.

## Non-Negotiable Architecture
- Blender add-on is the local UI/context/tool execution layer.
- Node.js + TypeScript is the backend.
- PostgreSQL is the durable application database.
- Redis/BullMQ is for asynchronous jobs only.
- AI providers are behind an abstraction.
- Scene operations use deterministic structured tools.
- Model output never directly executes arbitrary Blender Python.
- Every write action is validated and classified.
- Approval is required for meaningful modifications.
- RAG is separate from action tools.
- Coding agents are separate from the scene agent.
- Cursor SDK is a coding-agent provider, not the core scene engine.
- BYOK and managed credentials use the same provider abstraction.

## Before Every Phase
1. Read all planning documents.
2. Identify assumptions that may now be stale.
3. Inspect the current repository.
4. Identify contradictions/missing requirements.
5. Produce a concise implementation plan.
6. Define interfaces/contracts.
7. Define tests.
8. Ask for approval if the requested phase materially changes architecture.

## During Implementation
- Make small, reviewable changes.
- Do not overwrite unrelated work.
- Keep secrets out of source control.
- Add tests with each feature.
- Use typed contracts.
- Validate all external input.
- Log safely without secrets.
- Keep provider-specific code isolated.
- Keep Blender API version-specific code isolated.

## Phase Completion Checklist
- [ ] Code implemented
- [ ] Tests implemented/passing
- [ ] Documentation updated
- [ ] Manual validation completed
- [ ] Security implications reviewed
- [ ] Known limitations recorded
- [ ] Next phase defined

## Phase 1 Task
Start with the repository/add-on foundation only.

Do not implement the AI agent, provider calls, tool execution or billing in Phase 1.

Produce:
- repository structure
- Blender add-on package
- registration/unregistration
- native AI Workspace panel shell
- configuration/state module
- API-client interface stub
- logging/error abstraction
- test strategy and initial tests
- developer setup documentation
- CI baseline

At the end, stop and report exactly what changed, tests run, known limitations and the proposed Phase 2 plan.
