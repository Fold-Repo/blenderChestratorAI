import type {
  AIProvider,
  ProviderTurn,
  SceneProviderRequest,
} from './types.js';

/**
 * Local development provider. It is deliberately narrow and exists so the
 * agent loop can be tested without sending scene data to an external service.
 */
export class RuleBasedSceneProvider implements AIProvider {
  public readonly name = 'local-rule-based';

  async respond(request: SceneProviderRequest): Promise<ProviderTurn> {
    if (request.toolResults.length > 0) {
      const [firstResult] = request.toolResults;
      if (firstResult) {
        const proposal = proposalFromRequest(
          request.message,
          firstResult.result,
        );
        if (proposal) return proposal;
        return {
          type: 'assistant',
          message: summarizeResult(firstResult.result),
        };
      }
    }

    const message = request.message.toLowerCase();
    if (message.includes('hello backend')) {
      return {
        type: 'assistant',
        message: 'Hello backend! I am ready to help you.',
      };
    }
    if (
      /(how many|count|number of).*(objects|items)|object count/.test(message)
    ) {
      return call('get_scene_summary', {});
    }
    if (/(what|which|show|list).*(selected)|selected objects/.test(message)) {
      return call('get_selected_objects', {});
    }
    const movementMatch = message.match(
      /(?:move|translate)\s+(?:all\s+)?(.+?)\s+\d+(?:\.\d+)?\s*(?:m|met(?:er|re)s?)\s+(?:left|right|up|down)/,
    );
    if (movementMatch?.[1]) {
      const target = movementMatch[1].trim();
      return call('find_objects', {
        contains: target.endsWith('s') ? target.slice(0, -1) : target,
      });
    }
    const findMatch = message.match(
      /(?:find|search for|objects? named)\s+(.+)/,
    );
    const query = findMatch?.[1];
    if (query) {
      return call('find_objects', {
        contains: query.replace(/[?.!]+$/, '').trim(),
      });
    }

    return {
      type: 'assistant',
      message:
        'I can inspect the scene, selected objects, or find objects by name. Please make the request more specific.',
    };
  }
}

const call = (
  name: string,
  arguments_: Record<string, unknown>,
): ProviderTurn => ({
  type: 'tool_call',
  call: { callId: `local_${name}`, name, arguments: arguments_ },
});

const summarizeResult = (result: unknown): string => {
  if (!isRecord(result)) return 'The scene tool returned an invalid result.';
  if (typeof result.object_count === 'number') {
    return `There are ${result.object_count} objects in the current scene.`;
  }
  if (Array.isArray(result.objects) && typeof result.count === 'number') {
    if (result.count === 0) return 'No matching objects were found.';
    const names = result.objects
      .map((item) =>
        isRecord(item) && typeof item.name === 'string' ? item.name : null,
      )
      .filter((name): name is string => name !== null);
    return `Found ${result.count} object${result.count === 1 ? '' : 's'}: ${names.join(', ')}.`;
  }
  return 'The scene tool completed.';
};

const proposalFromRequest = (
  message: string,
  result: unknown,
): ProviderTurn | null => {
  const locationDelta = locationDeltaFromMessage(message.toLowerCase());
  if (!locationDelta || !isRecord(result) || !Array.isArray(result.objects)) {
    return null;
  }
  const objectIds = result.objects
    .map((item) =>
      isRecord(item) && typeof item.id === 'string' ? item.id : null,
    )
    .filter((id): id is string => id !== null);
  if (objectIds.length === 0) return null;
  return call('modify_object_transform', {
    object_ids: objectIds,
    location_delta: locationDelta,
  });
};

const locationDeltaFromMessage = (
  message: string,
): [number, number, number] | null => {
  const distanceMatch = message.match(/(\d+(?:\.\d+)?)\s*(?:m|met(?:er|re)s?)/);
  const distance = Number(distanceMatch?.[1] ?? 1);
  if (!Number.isFinite(distance) || distance <= 0) return null;
  if (/(move|translate).*(left)/.test(message)) return [-distance, 0, 0];
  if (/(move|translate).*(right)/.test(message)) return [distance, 0, 0];
  if (/(move|translate).*(up)/.test(message)) return [0, 0, distance];
  if (/(move|translate).*(down)/.test(message)) return [0, 0, -distance];
  return null;
};

const isRecord = (value: unknown): value is Record<string, unknown> =>
  typeof value === 'object' && value !== null && !Array.isArray(value);
