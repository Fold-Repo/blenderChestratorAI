# System Architecture

## Logical Architecture

```text
Blender Add-on
 ├─ Chat UI
 ├─ Context Collector
 ├─ Tool Registry
 ├─ Policy/Validation
 ├─ Preview/Approval
 └─ API Client
          │ HTTPS + streaming
          ▼
      Agent Gateway
          │
          ▼
    Agent Supervisor
      ├── Scene Agent
      ├── Knowledge/RAG Agent
      └── Coding Agent
          │
          ├── Provider Adapter → OpenAI
          ├── Provider Adapter → Anthropic
          └── Provider Adapter → Gemini

Backend
 ├─ Auth
 ├─ Projects
 ├─ Conversations
 ├─ Agents
 ├─ Providers/Credentials
 ├─ RAG
 ├─ Jobs
 ├─ Usage
 ├─ Billing
 └─ Audit
      ├─ PostgreSQL
      ├─ Redis/BullMQ
      └─ Object Storage
```

## Important Change
The original concept placed much of the security boundary in the add-on. The selected design makes the boundary explicit in both places:
- backend policy decides whether a proposed action is allowed;
- add-on validates again immediately before Blender execution.

This is defense in depth.

## Communication
REST for commands and resource APIs. SSE is preferred for MVP streaming because the dominant flow is server-to-client event streaming; WebSocket can be introduced where bidirectional low-latency events become necessary.

## Trust Boundaries
1. User ↔ add-on.
2. Add-on ↔ backend.
3. Backend ↔ model provider.
4. Backend ↔ project storage.
5. Coding agent ↔ workspace.
6. Backend ↔ provider credentials.

No model output crosses a trust boundary directly into privileged execution.
