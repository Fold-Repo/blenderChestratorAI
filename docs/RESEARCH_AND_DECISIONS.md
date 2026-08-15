# Research and Architecture Decision Record

## Verified External Findings — August 14, 2026

### Blender
Blender supports Python add-ons through its Python API and add-on registration system. Current Blender documentation includes scripting/extending guidance and an Extensions system. Blender's scripting security documentation warns that Python embedded in blend files is a security risk and automatic execution is disabled by default. Therefore project files must be treated as untrusted input.

### OpenAI
OpenAI currently recommends the Responses API for agentic workflows and provides tool-oriented agent building blocks. Current published API pricing should be treated as a launch-time variable rather than hardcoded business assumptions.

### Anthropic
Anthropic currently offers Claude through its API and Claude Code. Current Sonnet 5 pricing is temporarily promotional through August 31, 2026, after which standard pricing changes. This is a strong reason to keep provider pricing configurable.

### Gemini
Google's Gemini Interactions API became generally available in June 2026 and is positioned as the recommended interface for new Gemini projects, including tool orchestration and agentic workflows. Gemini supports function calling.

### Cursor
Cursor introduced a public-beta Cursor SDK in April 2026, with programmatic agents through `@cursor/sdk`. Cursor documents local/cloud runtimes, streaming, MCP/custom tools and agent lifecycle features. The SDK is therefore technically viable as a coding-agent adapter, but commercial/embedding terms must be verified before production customer use.

## Architectural Changes From Initial Concept
1. Add a second validation boundary in the add-on.
2. Make SSE the initial streaming choice; reserve WebSocket for true bidirectional needs.
3. Use capability-based provider adapters.
4. Delay queues until asynchronous workloads actually exist.
5. Delay RAG until the scene loop works.
6. Treat Cursor SDK as a coding-agent adapter.
7. Build a coding-agent interface before integrating Cursor.
8. Keep arbitrary Python/shell disabled in MVP.
9. Use a native Blender UI first instead of a web UI embedded in Blender.
10. Make pricing configurable and usage-driven.

## Commercial/Legal Note
Blender itself is GPL-licensed. Add-on licensing and distribution need a legal review based on the exact dependency/import/distribution structure and any Blender APIs/source code incorporated into the product. Do not assume that “commercial add-on” automatically means every distribution arrangement is legally equivalent. Provider SDK/API terms also need review before resale/embedding.

## Sources
- Blender Developer Documentation: https://developer.blender.org/docs/license
- Blender Manual scripting/security: https://docs.blender.org/manual/en/latest/advanced/scripting/security.html
- OpenAI API: https://openai.com/api/
- OpenAI pricing: https://openai.com/api/pricing/
- Cursor SDK announcement: https://cursor.com/changelog/sdk-release
- Gemini Interactions API: https://ai.google.dev/gemini-api/docs/interactions-overview
- Gemini function calling: https://ai.google.dev/gemini-api/docs/function-calling
- Anthropic API: https://www.anthropic.com/claude/api
