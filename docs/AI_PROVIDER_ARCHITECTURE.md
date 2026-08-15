# AI Provider Architecture

## Provider Interface
```ts
interface AIProvider {
  chat(request): Promise<Response>
  stream(request): AsyncIterable<Event>
  toolCall(request): Promise<ToolCallResult>
  estimateCost(request): Promise<CostEstimate>
  validateCredentials(credentials): Promise<CredentialStatus>
}
```

The real implementation should use a capability model rather than assuming all providers expose identical features.

## Initial Providers
- OpenAI
- Anthropic
- Gemini

OpenAI currently positions the Responses API as its agentic API primitive and provides tool-oriented agent building blocks. Gemini's Interactions API is currently GA and supports model/agent interactions, tool orchestration and background execution. Cursor SDK is treated separately as a coding-agent runtime.

## Capability Matrix
Each provider adapter declares:
- structured tool calling
- streaming
- vision/multimodal
- long context
- server-side conversation state
- background execution
- batch processing
- caching
- cost estimation
- data residency options

## Selection
The application chooses a provider/model through policy:
- user preference
- task type
- latency
- capability
- budget
- plan
- BYOK availability

Never bake a provider-specific message format into core domain objects.
