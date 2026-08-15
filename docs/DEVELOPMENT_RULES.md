# Development Rules

1. Do not code the whole product at once.
2. Before implementation, review architecture and identify contradictions.
3. Produce a phase-specific plan before coding.
4. Define interfaces/contracts before implementations.
5. Define tests before declaring completion.
6. Prefer deterministic Blender tools over generated Python.
7. Never trust model-generated tool arguments.
8. Never expose secrets unnecessarily.
9. Keep RAG separate from action execution.
10. Keep Cursor IDE, Cursor Agent, Cursor SDK and model APIs conceptually separate.
11. Version tool schemas.
12. Preserve backward compatibility.
13. Every write action has a permission class.
14. Destructive actions require explicit approval.
15. Keep project scope explicit in every privileged operation.
16. Make asynchronous jobs recoverable and idempotent.
17. End each phase with code, tests, docs, validation, limitations and next phase.
18. Record architectural decisions as ADRs.
19. Re-check external provider capabilities/pricing before implementation of provider-specific features.
20. Do not expand product scope without an explicit product decision.
