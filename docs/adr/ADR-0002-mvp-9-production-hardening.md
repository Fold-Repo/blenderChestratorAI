# ADR-0002: MVP-9 Production Hardening

## Status
Accepted

## Date
2026-08-15

## Context
MVP-9 needs a controlled-beta boundary: users, project isolation, usage/audit visibility, and basic request abuse controls. Persistent identity, billing, and SSO remain out of scope.

## Decision
Keep authentication and metering in the existing in-memory backend:

- Register/login issue opaque session tokens stored in add-on preferences.
- Every project has an `ownerId`; non-owners receive `404`.
- Runs write usage records and tool audit events; the add-on posts UI audit events for preview/apply/cancel/undo.
- Apply an in-process IP rate limiter and a 1MB JSON body limit.
- Redact secret-shaped fields in logs and audit metadata.
- Package the add-on with `scripts/package_addon.py`.

## Consequences
Pros:

- Beta testers can log in from Blender and only see their own work.
- Usage and audit endpoints exist for operator review without a database.
- Request abuse and secret leakage have a first control layer.

Trade-offs:

- Users, tokens, usage, and audit logs reset when the process restarts.
- Passwords are SHA-256 hashed without salt; tokens do not expire.
- Rate limits are per process and per IP, not a shared gateway.

## Scope Guardrails
Not implemented in MVP-9:

- PostgreSQL persistence
- salted/iterated password hashing, JWT expiry, refresh tokens
- billing, subscriptions, and cost caps
- RAG, BYOK, Cursor SDK, coding agents
- SSE streaming
