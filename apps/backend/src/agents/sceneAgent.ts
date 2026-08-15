import { AppError } from '../lib/errors.js';
import type {
  AIProvider,
  SceneProviderRequest,
  SceneToolDefinition,
} from '../providers/types.js';
import {
  type ModificationProposal,
  createModificationProposal,
} from './modificationProposal.js';

type JsonRecord = Record<string, unknown>;

export interface SceneAgentResult {
  assistantMessage: string;
  status: 'completed' | 'waiting_for_approval';
  toolCalls: Array<{ name: string; result: unknown }>;
  stateHistory: string[];
  proposal?: ModificationProposal;
}

const MAX_TOOL_CALLS = 2;
const SCENE_TOOLS: SceneToolDefinition[] = [
  {
    name: 'get_scene_summary',
    description: 'Get active-scene metadata and object counts.',
    inputSchema: emptySchema(),
  },
  {
    name: 'modify_object_transform',
    description:
      'Propose a bounded object transform. This always requires user approval and never executes a scene change.',
    inputSchema: transformSchema(),
  },
  {
    name: 'get_selected_objects',
    description: 'Get selected object identifiers and properties.',
    inputSchema: emptySchema(),
  },
  {
    name: 'find_objects',
    description:
      'Find objects using exact_name, contains, type, or collection.',
    inputSchema: findSchema(),
  },
];

export class SceneAgent {
  constructor(private readonly provider: AIProvider) {}

  async run(message: string, sceneContext: unknown): Promise<SceneAgentResult> {
    let state = 'running';
    const stateHistory = ['queued', state];
    const toolCalls: SceneAgentResult['toolCalls'] = [];
    const toolResults: SceneProviderRequest['toolResults'] = [];

    for (let count = 0; count <= MAX_TOOL_CALLS; count += 1) {
      const turn = await this.provider.respond({
        message,
        tools: SCENE_TOOLS,
        toolResults,
      });
      if (turn.type === 'assistant') {
        if (!turn.message.trim())
          throw new AppError(
            'MODEL_OUTPUT_INVALID',
            'Provider returned an empty assistant message.',
            502,
          );
        state = 'completed';
        stateHistory.push(state);
        return {
          assistantMessage: turn.message.trim(),
          status: 'completed',
          toolCalls,
          stateHistory,
        };
      }
      if (count === MAX_TOOL_CALLS) {
        throw new AppError(
          'TOOL_CALL_LIMIT_EXCEEDED',
          'The agent exceeded the tool-call limit.',
          502,
        );
      }
      if (!SCENE_TOOLS.some((tool) => tool.name === turn.call.name)) {
        throw new AppError(
          'TOOL_NOT_ALLOWED',
          'The provider requested a tool that is not allow-listed.',
          502,
        );
      }
      if (turn.call.name === 'modify_object_transform') {
        const proposal = createModificationProposal(
          turn.call.arguments,
          sceneContext,
        );
        toolCalls.push({ name: turn.call.name, result: proposal });
        state = 'waiting_for_approval';
        stateHistory.push(state);
        return {
          assistantMessage: `Prepared a transform proposal for ${proposal.targets.length} object${proposal.targets.length === 1 ? '' : 's'}. Approval is required before any scene change.`,
          status: 'waiting_for_approval',
          toolCalls,
          stateHistory,
          proposal,
        };
      }
      state = 'waiting_for_tool';
      stateHistory.push(state);
      const result = executeReadOnlyTool(
        turn.call.name,
        turn.call.arguments,
        sceneContext,
      );
      toolCalls.push({ name: turn.call.name, result });
      toolResults.push({ callId: turn.call.callId, result });
      state = 'running';
      stateHistory.push(state);
    }
    throw new AppError('AGENT_FAILED', 'The agent did not complete.', 502);
  }
}

const executeReadOnlyTool = (
  name: string,
  arguments_: unknown,
  sceneContext: unknown,
): unknown => {
  const context = asRecord(
    sceneContext,
    'SCENE_CONTEXT_INVALID',
    'A valid scene context is required.',
  );
  if (name === 'get_scene_summary') {
    requireEmptyArguments(arguments_);
    return asRecord(
      context.scene,
      'SCENE_CONTEXT_INVALID',
      'Scene summary is unavailable.',
    );
  }
  if (name === 'get_selected_objects') {
    requireEmptyArguments(arguments_);
    const objects = Array.isArray(context.objects) ? context.objects : [];
    const selectedIds = asRecord(
      context.selection,
      'SCENE_CONTEXT_INVALID',
      'Selection is unavailable.',
    ).selected_object_ids;
    const ids = Array.isArray(selectedIds)
      ? new Set(
          selectedIds.filter((id): id is string => typeof id === 'string'),
        )
      : new Set<string>();
    const selected = objects.filter(
      (object) =>
        isRecord(object) && typeof object.id === 'string' && ids.has(object.id),
    );
    return { objects: selected, count: selected.length };
  }
  if (name === 'find_objects') return findObjects(arguments_, context);
  throw new AppError(
    'TOOL_NOT_ALLOWED',
    'The requested tool is not allow-listed.',
    502,
  );
};

const findObjects = (arguments_: unknown, context: JsonRecord): JsonRecord => {
  const filters = asRecord(
    arguments_,
    'INVALID_TOOL_ARGUMENTS',
    'Tool arguments must be an object.',
  );
  const allowed = new Set(['exact_name', 'contains', 'type', 'collection']);
  if (
    Object.keys(filters).length === 0 ||
    Object.keys(filters).some((key) => !allowed.has(key))
  ) {
    throw new AppError(
      'INVALID_TOOL_ARGUMENTS',
      'Provide one or more supported search filters.',
      502,
    );
  }
  for (const value of Object.values(filters)) {
    if (typeof value !== 'string' || !value.trim())
      throw new AppError(
        'INVALID_TOOL_ARGUMENTS',
        'Search filters must be non-empty strings.',
        502,
      );
  }
  const objects = Array.isArray(context.objects)
    ? context.objects.filter(isRecord)
    : [];
  const matches = objects.filter((object) => {
    const name = typeof object.name === 'string' ? object.name : '';
    const type = typeof object.type === 'string' ? object.type : '';
    const collections = Array.isArray(object.collections)
      ? object.collections
      : [];
    const exactName = stringFilter(filters, 'exact_name');
    const contains = stringFilter(filters, 'contains');
    const typeFilter = stringFilter(filters, 'type');
    const collection = stringFilter(filters, 'collection');
    return (
      (!exactName || name === exactName) &&
      (!contains || name.toLowerCase().includes(contains.toLowerCase())) &&
      (!typeFilter || type === typeFilter) &&
      (!collection || collections.includes(collection))
    );
  });
  return { objects: matches, count: matches.length, filters };
};

const requireEmptyArguments = (value: unknown): void => {
  if (!isRecord(value) || Object.keys(value).length !== 0)
    throw new AppError(
      'INVALID_TOOL_ARGUMENTS',
      'This tool does not accept arguments.',
      502,
    );
};
const asRecord = (
  value: unknown,
  code: string,
  message: string,
): JsonRecord => {
  if (!isRecord(value)) throw new AppError(code, message, 502);
  return value;
};
const isRecord = (value: unknown): value is JsonRecord =>
  typeof value === 'object' && value !== null && !Array.isArray(value);
const stringFilter = (filters: JsonRecord, key: string): string | undefined => {
  const value = filters[key];
  return typeof value === 'string' ? value : undefined;
};
function emptySchema(): JsonRecord {
  return { type: 'object', additionalProperties: false, properties: {} };
}
function findSchema(): JsonRecord {
  return {
    type: 'object',
    additionalProperties: false,
    properties: {
      exact_name: { type: 'string' },
      contains: { type: 'string' },
      type: { type: 'string' },
      collection: { type: 'string' },
    },
  };
}
function transformSchema(): JsonRecord {
  return {
    type: 'object',
    additionalProperties: false,
    required: ['object_ids'],
    properties: {
      object_ids: { type: 'array', items: { type: 'string' } },
      location_delta: { type: 'array', items: { type: 'number' } },
      rotation_delta: { type: 'array', items: { type: 'number' } },
      scale_multiplier: { type: 'array', items: { type: 'number' } },
    },
  };
}
