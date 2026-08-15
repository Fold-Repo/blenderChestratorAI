import {
  type AIProvider,
  ProviderError,
  type ProviderTurn,
  type SceneProviderRequest,
} from './types.js';

interface OpenAIResponsesProviderOptions {
  apiKey: string;
  model?: string;
  fetchImpl?: typeof fetch;
}

/** OpenAI Responses API adapter. Core agent code only sees the AIProvider interface. */
export class OpenAIResponsesProvider implements AIProvider {
  public readonly name = 'openai-responses';
  private readonly model: string;
  private readonly fetchImpl: typeof fetch;

  constructor(private readonly options: OpenAIResponsesProviderOptions) {
    this.model = options.model ?? 'gpt-5-mini';
    this.fetchImpl = options.fetchImpl ?? fetch;
  }

  async respond(request: SceneProviderRequest): Promise<ProviderTurn> {
    const input = request.toolResults.length
      ? request.toolResults.map((item) => ({
          type: 'function_call_output',
          call_id: item.callId,
          output: JSON.stringify(item.result),
        }))
      : request.message;
    const response = await this.fetchImpl(
      'https://api.openai.com/v1/responses',
      {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${this.options.apiKey}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          model: this.model,
          store: false,
          instructions:
            'You are a Blender scene assistant. Use only the supplied tools. Never request code or shell commands. modify_object_transform creates an approval-required proposal only; it never executes a scene change. Return a concise answer after read-only tool results.',
          input,
          tools: request.tools.map((tool) => ({
            type: 'function',
            name: tool.name,
            description: tool.description,
            parameters: tool.inputSchema,
            strict: true,
          })),
        }),
      },
    );
    if (!response.ok)
      throw new ProviderError(
        `OpenAI request failed with status ${response.status}.`,
      );

    const payload: unknown = await response.json();
    if (!isRecord(payload) || !Array.isArray(payload.output)) {
      throw new ProviderError('OpenAI returned an invalid response payload.');
    }
    const call = payload.output.find(
      (item) => isRecord(item) && item.type === 'function_call',
    );
    if (
      isRecord(call) &&
      typeof call.name === 'string' &&
      typeof call.call_id === 'string'
    ) {
      if (typeof call.arguments !== 'string')
        throw new ProviderError('Tool call arguments were not JSON.');
      try {
        return {
          type: 'tool_call',
          call: {
            callId: call.call_id,
            name: call.name,
            arguments: JSON.parse(call.arguments),
          },
        };
      } catch {
        throw new ProviderError('Tool call arguments were invalid JSON.');
      }
    }
    if (typeof payload.output_text === 'string' && payload.output_text.trim()) {
      return { type: 'assistant', message: payload.output_text.trim() };
    }
    throw new ProviderError(
      'OpenAI returned neither a tool call nor an assistant message.',
    );
  }
}

const isRecord = (value: unknown): value is Record<string, unknown> =>
  typeof value === 'object' && value !== null && !Array.isArray(value);
