# API Specification

## MVP Endpoints

All routes below are served under `/api/v1`.

### Health
`GET /health`
`GET /api/v1/health`

Unauthenticated. Used for process and add-on connection checks.

### Authentication
`POST /api/v1/auth/register`
`POST /api/v1/auth/login`

Register and login return `{ user, token, requestId }`. The token is a bearer session token sent as `Authorization: Bearer <token>`.

### Projects
`GET /api/v1/projects`
`POST /api/v1/projects`
`GET /api/v1/projects/:id`

Authenticated. Results are limited to the caller's owned projects.

### Chat
`POST /api/v1/projects/:id/conversations`
`POST /api/v1/conversations/:id/runs`

Authenticated and project-scoped. Creating a run records usage and tool audit events.

`GET /v1/runs/:id/events` — SSE (not implemented in MVP-9)

### Usage
`GET /api/v1/usage`

Authenticated. Returns the caller's run usage records (provider, model, tool-call count, estimated cost).

### Audit
`POST /api/v1/audit-logs`
`GET /api/v1/audit-logs`

Authenticated. The add-on posts preview/apply/cancel/undo events. Secrets in `parametersMetadata` are redacted.

### Providers
`GET /v1/providers`
`POST /v1/provider-credentials`
`POST /v1/provider-credentials/:id/validate`

Deferred. MVP-9 uses the local rule-based provider, or OpenAI when `OPENAI_API_KEY` is set.

## Event Schema
```json
{
  "id": "event-id",
  "run_id": "run-id",
  "sequence": 12,
  "type": "tool.completed",
  "timestamp": "...",
  "payload": {}
}
```

## Required Event Types
- message.delta
- tool.started
- tool.completed
- action.proposed
- action.approval_required
- action.approved
- action.rejected
- execution.started
- execution.completed
- run.completed
- run.failed

## API Rules
- versioned endpoints
- idempotency keys for mutation endpoints, scoped per authenticated user
- authenticated project scope
- request size limits (`1mb` JSON)
- rate limits (in-memory, health excluded)
- structured errors
- correlation/request IDs
- secret redaction in logs and audit metadata
