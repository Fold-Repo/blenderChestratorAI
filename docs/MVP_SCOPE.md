# MVP Scope

## In Scope
- Blender add-on
- native chat UI
- authentication
- project registration
- one AI provider
- structured scene context
- five tools
- tool calling
- safe transform proposal
- preview
- approval
- execution
- undo/recovery
- basic usage tracking
- audit events
- basic provider configuration

## Out of Scope
- Cursor SDK production integration
- arbitrary Python execution
- shell execution
- full RAG
- team management
- enterprise SSO
- advanced billing
- multi-application connectors
- autonomous long-running scene agents
- dozens of tools
- full asset pipeline automation

## MVP Demo
1. User opens Blender.
2. Opens Copilot.
3. Asks “Find all objects named Tree.”
4. Agent calls `find_objects`.
5. Agent reports count.
6. User asks to select them.
7. Agent calls `select_objects`.
8. User asks to move them 2m left.
9. Agent creates a structured proposal.
10. User previews and approves.
11. Tool executes.
12. User can undo.
