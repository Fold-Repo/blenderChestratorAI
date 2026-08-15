# Agent Architecture

## Supervisor
The supervisor classifies requests and selects:
- Scene Agent
- Knowledge Agent
- Coding Agent

It must not execute Blender operations itself.

## Scene Agent
Responsibilities:
- interpret natural language
- request relevant context
- select structured Blender tools
- reason over tool results
- create action proposals
- explain outcomes

## Knowledge Agent
Responsibilities:
- retrieve project/company documentation
- retrieve Blender/API knowledge
- return cited knowledge to the reasoning layer
- never execute Blender actions

## Coding Agent
Responsibilities:
- inspect approved workspace
- modify code
- run approved tests
- return patch/change set
- never directly mutate the production Blender scene without the explicit scene execution path

## Agent Run State
```text
queued
running
waiting_for_tool
waiting_for_approval
executing
completed
failed
cancelled
```

## Guardrails
- maximum tool calls per turn
- maximum execution duration
- tool allowlist
- project scope
- user permission scope
- output validation
- loop detection
- cancellation
- audit logging

## Orchestration
Start with one supervisor and one scene agent. Introduce multi-agent delegation only when a real workflow needs it.
