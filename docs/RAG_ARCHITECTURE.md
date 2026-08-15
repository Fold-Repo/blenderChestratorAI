# RAG Architecture

## Purpose
RAG provides knowledge. It does not execute actions.

## Sources
- project documentation
- approved Python files
- company standards
- internal guidelines
- Blender documentation
- asset metadata
- previous approved AI decisions
- user instructions

## Pipeline
```text
Source
 → parser
 → chunker
 → metadata
 → embedding
 → vector store
 → retrieval
 → reranking
 → grounded context
 → agent
```

## Security
Documents are untrusted. Retrieved text must never be treated as executable instructions merely because it appears in a trusted knowledge source.

## MVP
No large RAG system. Define interfaces and ingest only a small controlled project knowledge set after the scene-agent loop works.

## Separation
RAG answers “what should/does this mean?”
Tools answer “what can the system do?”
