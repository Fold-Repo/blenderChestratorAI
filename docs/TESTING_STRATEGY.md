# Testing Strategy

## Add-on
- unit tests for serializers and validators
- context collector tests
- tool tests
- Blender integration tests
- registration/unregistration tests
- undo tests

## Backend
- unit tests
- API contract tests
- provider adapter tests
- agent policy tests
- database tests
- queue tests
- credential handling tests

## Agent Evaluation
Create deterministic scenarios:
- exact object lookup
- ambiguous object request
- missing object
- transform request
- destructive request
- malicious project instruction
- provider failure
- tool validation failure

## End-to-End
Chat → tool call → result → proposal → approval → execution → result → undo.

## Security
Test:
- prompt injection
- malformed tool arguments
- oversized payloads
- unauthorized project IDs
- credential exposure
- path traversal
- shell escape
- replay/idempotency
- rate-limit bypass.

## Quality Gate
No phase is complete until tests, documentation, manual validation and known limitations are recorded.
