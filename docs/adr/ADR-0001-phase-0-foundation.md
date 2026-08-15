# ADR-0001: MVP-0 Repository Foundation

## Status
Accepted

## Date
2026-08-14

## Context
MVP-0 requires a development-ready monorepo that establishes baseline build, test, CI, error/logging abstractions, and a Blender add-on shell without implementing AI functionality.

## Decision
Adopt a monorepo with:

- `apps/backend` for Node.js/TypeScript API shell
- `apps/blender_addon` for Blender Python add-on shell
- `packages/contracts` for shared TypeScript API contracts

Implement only:

- backend health endpoints
- logging and error abstraction
- Blender panel registration/unregistration shell
- CI pipeline with lint/typecheck/test/build

## Consequences
Pros:

- clear package boundaries early
- deterministic path for MVP-1 onward
- fast onboarding with one workspace and one CI workflow

Trade-offs:

- backend and contracts are intentionally minimal and will expand later
- Blender UI is shell-only and does not yet provide interaction features

## Scope Guardrails
Not implemented in MVP-0:

- provider integrations
- RAG
- BYOK
- billing/subscriptions
- Cursor SDK integration
- arbitrary Python/shell execution
