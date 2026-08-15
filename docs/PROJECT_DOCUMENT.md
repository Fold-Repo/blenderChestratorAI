# Blender AI Copilot — Project Document

## 1. Executive Summary
Blender AI Copilot is a Blender-native AI assistant delivered as a Blender add-on plus a cloud/backend platform. Its defining capability is not generic chat, but grounded interaction with a live Blender project through a controlled tool system.

The product will initially focus exclusively on Blender. Other creative applications are future connectors and are outside the initial implementation.

## 2. Product Thesis
The assistant should understand the user's scene, project context, development files and project knowledge, then reason about requests and invoke deterministic tools. AI proposes; policy validates; Blender executes.

## 3. Architecture Decision
Selected architecture:
- Blender Python add-on for UI, local context collection, tool execution, validation, preview and approval.
- TypeScript/Node.js backend for authentication, conversations, agent orchestration, providers, usage, projects and billing.
- PostgreSQL for durable application data.
- Redis/BullMQ only for asynchronous work.
- Provider abstraction for OpenAI, Anthropic and Gemini.
- Separate coding-agent abstraction, with Cursor SDK as one provider rather than the core scene agent.
- RAG separated from action tools.
- BYOK and managed AI supported through the same provider abstraction.

## 4. Key Design Principle
Never allow an LLM to directly execute arbitrary Blender Python when a deterministic structured tool can perform the operation.

Flow:
User → Supervisor/Scene Agent → structured tool call → validation/policy → preview/approval → Blender API → result → agent explanation.

## 5. MVP
The MVP proves:
1. Installable Blender add-on.
2. Embedded chat.
3. Authentication.
4. Backend chat endpoint.
5. One managed AI provider.
6. Structured scene context.
7. Five core tools.
8. Tool-result loop.
9. Safe transform modification.
10. Preview and approval.
11. Undo/recovery.
12. Basic usage tracking.

## 6. Non-Goals
Do not initially build:
- multi-application support
- autonomous unrestricted Python execution
- full project indexing
- enterprise SSO
- complex billing tiers
- large RAG corpus
- coding-agent production integration
- dozens of Blender tools

## 7. Production Constraints
The platform must treat .blend files, scripts and project documents as untrusted input. Blender itself warns that Python embedded in blend files is a security risk and automatic execution is disabled by default. This reinforces the need for strict trust boundaries.

## 8. Success Metric
The first meaningful demo is:
“Find all objects named Tree” → identify objects → select them → propose “move them 2 metres left” → preview → approval → deterministic execution → undo.
