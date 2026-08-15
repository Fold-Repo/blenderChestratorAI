import { describe, expect, it } from 'vitest';
import { SceneAgent } from '../src/agents/sceneAgent.js';
import { RuleBasedSceneProvider } from '../src/providers/ruleBasedSceneProvider.js';
import {
  type AIProvider,
  ProviderError,
  type ProviderTurn,
  type SceneProviderRequest,
} from '../src/providers/types.js';

class ScriptedProvider implements AIProvider {
  public readonly name = 'scripted';
  private index = 0;

  constructor(private readonly turns: ProviderTurn[]) {}

  async respond(_request: SceneProviderRequest): Promise<ProviderTurn> {
    const turn = this.turns[this.index];
    this.index += 1;
    if (!turn) throw new ProviderError('No scripted turn remains.');
    return turn;
  }
}

const sceneContext = {
  scene: { scene_name: 'Demo', object_count: 3 },
  selection: { selected_object_ids: ['tree-1'] },
  objects: [
    { id: 'tree-1', name: 'Tree Oak', type: 'MESH', collections: ['Nature'] },
    { id: 'rock-1', name: 'Rock', type: 'MESH', collections: ['Nature'] },
    { id: 'camera-1', name: 'Camera', type: 'CAMERA', collections: [] },
  ],
};

const toolCall = (name: string, arguments_: unknown): ProviderTurn => ({
  type: 'tool_call',
  call: { callId: 'call-1', name, arguments: arguments_ },
});

describe('SceneAgent', () => {
  it('gets an object count through the scene-summary tool', async () => {
    const agent = new SceneAgent(
      new ScriptedProvider([
        toolCall('get_scene_summary', {}),
        { type: 'assistant', message: 'There are 3 objects.' },
      ]),
    );

    const result = await agent.run('How many objects are there?', sceneContext);

    expect(result.assistantMessage).toBe('There are 3 objects.');
    expect(result.toolCalls[0]?.result).toEqual(sceneContext.scene);
    expect(result.stateHistory).toEqual([
      'queued',
      'running',
      'waiting_for_tool',
      'running',
      'completed',
    ]);
  });

  it('handles selected, matching, and non-matching objects', async () => {
    const selected = new SceneAgent(
      new ScriptedProvider([
        toolCall('get_selected_objects', {}),
        { type: 'assistant', message: 'Tree Oak is selected.' },
      ]),
    );
    const found = new SceneAgent(
      new ScriptedProvider([
        toolCall('find_objects', { contains: 'Tree' }),
        { type: 'assistant', message: 'Found Tree Oak.' },
      ]),
    );
    const missing = new SceneAgent(
      new ScriptedProvider([
        toolCall('find_objects', { exact_name: 'Missing' }),
        { type: 'assistant', message: 'No objects found.' },
      ]),
    );

    await expect(
      selected.run('What is selected?', sceneContext),
    ).resolves.toMatchObject({
      toolCalls: [{ name: 'get_selected_objects', result: { count: 1 } }],
    });
    await expect(found.run('Find Tree', sceneContext)).resolves.toMatchObject({
      toolCalls: [{ name: 'find_objects', result: { count: 1 } }],
    });
    await expect(
      missing.run('Find Missing', sceneContext),
    ).resolves.toMatchObject({
      toolCalls: [{ name: 'find_objects', result: { count: 0 } }],
    });
  });

  it('returns a clarification for an ambiguous request without a tool call', async () => {
    const agent = new SceneAgent(
      new ScriptedProvider([
        { type: 'assistant', message: 'Do you want a count or a name search?' },
      ]),
    );

    await expect(
      agent.run('Help with the scene', sceneContext),
    ).resolves.toMatchObject({ toolCalls: [] });
  });

  it('rejects invalid tool arguments and disallowed tools', async () => {
    const invalid = new SceneAgent(
      new ScriptedProvider([toolCall('find_objects', {})]),
    );
    const disallowed = new SceneAgent(
      new ScriptedProvider([
        toolCall('select_objects', { object_ids: ['tree-1'] }),
      ]),
    );

    await expect(invalid.run('Find', sceneContext)).rejects.toMatchObject({
      code: 'INVALID_TOOL_ARGUMENTS',
    });
    await expect(
      disallowed.run('Select Tree', sceneContext),
    ).rejects.toMatchObject({ code: 'TOOL_NOT_ALLOWED' });
  });

  it('surfaces provider failures and detects a tool-call loop', async () => {
    const failure: AIProvider = {
      name: 'failed',
      respond: async () => {
        throw new ProviderError('Provider offline.');
      },
    };
    const loop = new SceneAgent(
      new ScriptedProvider([
        toolCall('get_scene_summary', {}),
        toolCall('get_scene_summary', {}),
        toolCall('get_scene_summary', {}),
      ]),
    );

    await expect(
      new SceneAgent(failure).run('Count', sceneContext),
    ).rejects.toThrow('Provider offline.');
    await expect(loop.run('Count', sceneContext)).rejects.toMatchObject({
      code: 'TOOL_CALL_LIMIT_EXCEEDED',
    });
  });

  it('creates an approval-required proposal without executing a modification', async () => {
    const agent = new SceneAgent(
      new ScriptedProvider([
        toolCall('find_objects', { contains: 'Tree' }),
        toolCall('modify_object_transform', {
          object_ids: ['tree-1'],
          location_delta: [-2, 0, 0],
        }),
      ]),
    );

    const result = await agent.run(
      'Move all trees 2 metres left.',
      sceneContext,
    );

    expect(result.status).toBe('waiting_for_approval');
    expect(result.proposal).toMatchObject({
      permissionLevel: 'APPROVAL_REQUIRED',
      status: 'awaiting_approval',
      locationDelta: [-2, 0, 0],
      targets: [{ id: 'tree-1', name: 'Tree Oak' }],
    });
    expect(result.toolCalls).toHaveLength(2);
    expect(result.stateHistory.at(-1)).toBe('waiting_for_approval');
  });

  it('uses the local provider to find targets before proposing a move', async () => {
    const result = await new SceneAgent(new RuleBasedSceneProvider()).run(
      'Move all trees 2 metres left.',
      sceneContext,
    );

    expect(result.status).toBe('waiting_for_approval');
    expect(result.toolCalls.map((call) => call.name)).toEqual([
      'find_objects',
      'modify_object_transform',
    ]);
    expect(result.proposal?.locationDelta).toEqual([-2, 0, 0]);
  });

  it('rejects unbounded, unknown, and no-op modification proposals', async () => {
    const invalid = (arguments_: unknown) =>
      new SceneAgent(
        new ScriptedProvider([toolCall('modify_object_transform', arguments_)]),
      ).run('Modify', sceneContext);

    await expect(
      invalid({ object_ids: ['missing'], location_delta: [-2, 0, 0] }),
    ).rejects.toMatchObject({ code: 'UNKNOWN_OBJECT_ID' });
    await expect(
      invalid({ object_ids: ['tree-1'], location_delta: [10_001, 0, 0] }),
    ).rejects.toMatchObject({ code: 'INVALID_TOOL_ARGUMENTS' });
    await expect(invalid({ object_ids: ['tree-1'] })).rejects.toMatchObject({
      code: 'INVALID_TOOL_ARGUMENTS',
    });
  });
});
