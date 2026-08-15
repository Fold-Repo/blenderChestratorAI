# Blender AI Copilot

Phase-0 through MVP-9 implementation for Blender AI Copilot.

## Repository Layout

- `apps/backend`: Node.js/TypeScript backend with auth, projects, scene agent, usage, and audit APIs
- `apps/blender_addon`: Blender add-on with chat, tools, preview/apply/undo, and login preferences
- `packages/contracts`: shared TypeScript API contracts
- `docs`: architecture and planning documents
- `scripts/package_addon.py`: release zip packaging for the add-on

## Supported versions

- Blender 4.2+
- Node.js 20+
- AI provider: local rule-based development provider by default; OpenAI Responses API when `OPENAI_API_KEY` is set

## Quick Start

### 1) Install dependencies

```bash
npm install
```

### 2) Run backend locally

```bash
npm run dev -w @blender-ai/backend
```

Health checks:

- `GET /health`
- `GET /api/v1/health`

Authenticated API routes require `Authorization: Bearer <token>` from `POST /api/v1/auth/register` or `/auth/login`.

### 3) Install the Blender add-on

Development:

1. Open Blender 4.2+.
2. **Edit > Preferences > Add-ons > Install...**
3. Zip the add-on with `python3 scripts/package_addon.py` and install `apps/blender_addon/blender_ai_copilot.zip`.
4. Enable **Blender AI Copilot**.
5. In add-on preferences, set backend URL (`http://localhost:3009`), username, and password, then click **Authenticate / Log In**.

### 4) Validate

```bash
npm run lint
npm run typecheck
npm run test
npm run build
```

## Environment

Copy `.env.example` values into your local environment as needed.

## Troubleshooting

- **Add-on shows Offline**: confirm the backend is running on the configured base URL and that `/api/v1/health` returns `ok`.
- **Authentication required / invalid token**: log in from add-on preferences. Tokens live in memory on the backend and are lost on restart.
- **Project not found**: the session belongs to a different user, or the backend process restarted and dropped in-memory data.
- **Rate limit exceeded**: wait for the `Retry-After` window (100 requests/minute/IP by default).
- **Request body too large**: JSON payloads over 1MB are rejected.

## MVP-9 Scope Notes

Implemented:

- monorepo scaffold
- backend health endpoint
- logging/error abstractions with secret redaction
- Blender Copilot workspace, chat, scene context, and tool executor
- backend-connected chat with timeout/retry and connection status
- provider-neutral scene-agent loop with OpenAI Responses API adapter
- approval-required transform proposals with preview, apply, cancel, and undo
- register/login session tokens stored in add-on preferences
- project ownership isolation
- usage tracking and audit logs
- in-memory rate limiting and 1MB JSON body limit
- add-on release packaging script
- CI workflow and test baseline

Not implemented:

- persistent database, SSO, token expiry
- multiple AI providers, BYOK, and provider credential management
- RAG
- billing and subscriptions
- SSE streaming
- Cursor SDK / coding agents
