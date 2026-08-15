# Database Plan

## MVP Entities
- User
- Project
- BlenderProject
- Conversation
- Message
- AgentRun
- ToolCall
- ToolResult
- AIProvider
- UserProviderCredential
- UsageRecord
- AuditLog

## Later
- Organization
- Job
- JobAttempt
- Document
- Embedding
- Subscription
- billing events
- project memberships

## Key Principles
- UUID identifiers
- created/updated timestamps
- soft deletion where required
- tenant/project scoping
- immutable audit events
- encrypted credential fields
- JSONB for provider/tool-specific metadata
- relational columns for query-critical data

## MVP Relationship
User → Projects → Conversations → AgentRuns → ToolCalls/Results.

Provider credentials belong to a user or organization and are referenced by provider ID and encrypted credential material.
