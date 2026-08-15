export interface SceneToolDefinition {
  name: string;
  description: string;
  inputSchema: Record<string, unknown>;
}

export interface ProviderToolCall {
  callId: string;
  name: string;
  arguments: unknown;
}

export type ProviderTurn =
  | { type: 'assistant'; message: string }
  | { type: 'tool_call'; call: ProviderToolCall };

export interface SceneProviderRequest {
  message: string;
  tools: SceneToolDefinition[];
  toolResults: Array<{ callId: string; result: unknown }>;
}

export interface AIProvider {
  readonly name: string;
  respond(request: SceneProviderRequest): Promise<ProviderTurn>;
}

export class ProviderError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'ProviderError';
  }
}
