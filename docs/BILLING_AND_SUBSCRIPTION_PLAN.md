# Billing and Subscription Plan

## Initial Business Model
Potential:
- Free: limited scene assistance + BYOK.
- Pro: managed AI + advanced features.
- Pro BYOK: platform subscription with user-funded provider usage.
- Team: shared projects and standards.
- Enterprise: private deployment, SSO and advanced controls.

## Important Decision
Do not finalize public prices from architecture assumptions. Model pricing from current provider costs, expected tokens/tool calls, infrastructure, support and gross-margin targets.

## Cost Drivers
- model input/output tokens
- tool-call volume
- RAG storage/retrieval
- background jobs
- object storage
- database
- queue
- observability
- coding-agent consumption

## Usage Metering
Record:
- provider
- model
- input tokens
- cached input
- output tokens
- tool calls
- job duration
- estimated cost
- billing category

## Current Pricing Snapshot
As of August 2026, current official sources show materially different provider economics. OpenAI's published API pricing lists GPT-5.6 variants from $1/$6 to $5/$30 per million input/output tokens under standard processing. Gemini offers free and paid tiers with model-specific token pricing and batch/caching options. Anthropic currently lists Sonnet 5 at an introductory $2/$10 through August 31, 2026, then $3/$15.

These numbers must be rechecked before launch.
