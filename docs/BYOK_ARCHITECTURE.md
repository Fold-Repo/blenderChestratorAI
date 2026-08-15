# BYOK Architecture

## Supported Model
Users can connect provider credentials while the platform can also offer managed AI.

## Managed
Blender → backend → provider using platform credentials.

## BYOK
Blender → backend → provider using a credential reference owned by the user.

The backend should not send raw secrets back to the Blender UI after initial setup.

## Credential Storage
Use:
- envelope encryption
- KMS/secret manager
- encrypted-at-rest database values only where necessary
- provider-specific credential validation
- access controls
- audit logs
- rotation/revocation

## Important Limitation
BYOK support should be capability-based. A provider may support API keys, OAuth or other credential mechanisms, and not every agent product supports the same authentication model.

## Cursor
Treat Cursor SDK credentials as a separate integration. Do not assume that a Cursor subscription automatically grants rights to embed Cursor agents into a SaaS product. Confirm commercial terms and API/SDK terms before enabling customer-facing production use.

## UX
Settings → Providers → Add credential → validate → select scope → store encrypted reference → test connection.
