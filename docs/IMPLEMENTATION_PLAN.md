# Implementation Plan

## Phase 0 — Architecture/Repository
Deliver:
- monorepo structure
- ADRs
- coding standards
- CI
- local dev environment
- environment contract
- initial security baseline

## Phase 1 — Add-on Skeleton
Deliver:
- installable add-on
- registration lifecycle
- native panel
- settings
- local state
- API client abstraction
- test harness

## Phase 2 — Chat UI
Deliver:
- conversation state
- composer
- message rendering
- errors
- cancellation
- placeholder streaming interface

## Phase 3 — Backend
Deliver:
- Node/TypeScript service
- auth
- project
- conversation/run models
- health
- first chat endpoint

## Phase 4 — Context Engine
Deliver deterministic scene summary and selected-object collectors.

## Phase 5 — Tool System
Implement five MVP tools and validators.

## Phase 6 — Provider Abstraction
Implement one provider end-to-end, then adapters.

## Phase 7 — Scene Agent
Implement structured tool-calling loop.

## Phase 8 — Approval/Preview
Implement proposals, approvals, execution and undo.

## Phase 9 — Streaming
Connect structured events to Blender UI.

## Phase 10+ 
Authentication hardening, RAG, jobs, coding-agent abstraction, Cursor, BYOK, billing, teams, security hardening, beta and production.

## Rule
Only one phase should be actively implemented at a time.
