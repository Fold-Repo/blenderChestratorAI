# Coding Standards (MVP Baseline)

## General

- Keep phase scope strict; do not pre-implement future phases.
- Prefer deterministic logic for scene operations.
- Favor explicit interfaces/contracts before implementation details.

## TypeScript

- `strict` mode is required.
- Avoid `any`; use `unknown` plus narrowing.
- Keep API responses typed in `packages/contracts`.
- Use structured logging for backend events.

## Python (Blender)

- Keep Blender-specific `bpy` usage isolated from generic logic.
- Ensure add-on `register`/`unregister` remains idempotent and safe.
- Keep UI shell minimal until MVP-1 and MVP-2.

## Testing

- Unit tests are required for every new module in MVP scope.
- Backend endpoint behavior must be tested via HTTP-level tests.
- Blender add-on shell should have Python unit tests that run outside Blender for baseline lifecycle safety.

## Security

- Never commit secrets.
- Treat all model or file content as untrusted input.
- Keep privileged actions behind explicit validation and approval when those features are introduced in later phases.
