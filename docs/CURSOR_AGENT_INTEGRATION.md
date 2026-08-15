# Cursor Agent Integration

## Role
Cursor is a coding-agent provider, not the scene agent.

## Current Verified Direction
Cursor introduced a public-beta SDK in 2026. The TypeScript SDK exposes programmatic agents and supports local/cloud runtimes. Cursor also documents custom tools, MCP integration, streaming and agent/run lifecycle features.

## Proposed Flow
User → Supervisor → Coding Agent Adapter → Cursor SDK → isolated workspace → tests/review → patch → approval → merge/apply → Blender reload/test.

## Workspace Rules
- dedicated project workspace
- no host-wide shell access by default
- explicit file allowlist
- network policy
- CPU/memory/time limits
- Git branch isolation
- patch-based review
- secrets excluded
- audit events

## MVP Decision
Do not integrate Cursor SDK during Phase 1. Build the coding-agent interface and a mock/local adapter first. Integrate Cursor only after the core tool/approval architecture is proven.

## Commercial Check
Before public production use, verify current Cursor SDK terms, pricing, redistribution/embedding rights and customer credential requirements.
