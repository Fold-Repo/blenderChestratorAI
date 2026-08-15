# Queue and Worker Architecture

## Principle
Real-time scene operations should not be forced through a job queue.

## Synchronous
- scene summary
- selected objects
- object search
- selection
- small transforms

## Asynchronous
- full project analysis
- indexing
- large asset processing
- LOD generation
- RAG ingestion
- coding-agent runs
- batch operations

## Technology
Redis + BullMQ is the initial candidate because the backend is Node.js/TypeScript.

## Job Contract
```text
job_id
type
project_id
attempt
status
idempotency_key
created_at
started_at
completed_at
error
result_reference
```

## Reliability
- retries with backoff
- idempotency
- dead-letter handling
- cancellation
- progress events
- timeout
- structured errors
- durable status

Do not introduce workers until an actual asynchronous workflow exists.
