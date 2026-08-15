import { randomUUID } from 'node:crypto';
import { AppError } from '../lib/errors.js';

type JsonRecord = Record<string, unknown>;

export interface ModificationProposal {
  id: string;
  toolName: 'modify_object_transform';
  toolVersion: '1';
  permissionLevel: 'APPROVAL_REQUIRED';
  status: 'awaiting_approval';
  sceneName: string;
  targets: Array<{ id: string; name: string; type: string }>;
  locationDelta: [number, number, number];
  rotationDelta: [number, number, number];
  scaleMultiplier: [number, number, number];
  risk: 'approval_required';
  createdAt: string;
}

const MAX_TARGETS = 50;
const MAX_LOCATION_DELTA = 1_000;
const MAX_ROTATION_DELTA = Math.PI * 2;
const MIN_SCALE = 0.01;
const MAX_SCALE = 100;

export const createModificationProposal = (
  arguments_: unknown,
  sceneContext: unknown,
): ModificationProposal => {
  const argumentsRecord = asRecord(
    arguments_,
    'INVALID_TOOL_ARGUMENTS',
    'Modification arguments must be an object.',
  );
  const allowed = new Set([
    'object_ids',
    'location_delta',
    'rotation_delta',
    'scale_multiplier',
  ]);
  if (
    Object.keys(argumentsRecord).some((key) => !allowed.has(key)) ||
    !('object_ids' in argumentsRecord)
  ) {
    throw new AppError(
      'INVALID_TOOL_ARGUMENTS',
      'object_ids is required and only transform fields are supported.',
      502,
    );
  }

  const objectIds = validateObjectIds(argumentsRecord.object_ids);
  const context = asRecord(
    sceneContext,
    'SCENE_CONTEXT_INVALID',
    'A valid scene context is required.',
  );
  const scene = asRecord(
    context.scene,
    'SCENE_CONTEXT_INVALID',
    'Scene metadata is unavailable.',
  );
  if (typeof scene.scene_name !== 'string' || !scene.scene_name) {
    throw new AppError(
      'SCENE_CONTEXT_INVALID',
      'Active scene name is unavailable.',
      502,
    );
  }

  const objects = Array.isArray(context.objects)
    ? context.objects.filter(isRecord)
    : [];
  const objectIndex = new Map<string, JsonRecord>();
  for (const object of objects) {
    if (typeof object.id !== 'string' || !object.id) continue;
    if (objectIndex.has(object.id)) {
      throw new AppError(
        'AMBIGUOUS_OBJECT_ID',
        'Scene contains duplicate object IDs.',
        502,
      );
    }
    objectIndex.set(object.id, object);
  }
  const missingIds = objectIds.filter((id) => !objectIndex.has(id));
  if (missingIds.length > 0) {
    throw new AppError(
      'UNKNOWN_OBJECT_ID',
      'One or more targets are not in the active scene.',
      502,
    );
  }

  const locationDelta = vector(
    argumentsRecord.location_delta,
    [0, 0, 0],
    MAX_LOCATION_DELTA,
    'location_delta',
  );
  const rotationDelta = vector(
    argumentsRecord.rotation_delta,
    [0, 0, 0],
    MAX_ROTATION_DELTA,
    'rotation_delta',
  );
  const scaleMultiplier = scaleVector(argumentsRecord.scale_multiplier);
  if (
    locationDelta.every((value) => value === 0) &&
    rotationDelta.every((value) => value === 0) &&
    scaleMultiplier.every((value) => value === 1)
  ) {
    throw new AppError(
      'INVALID_TOOL_ARGUMENTS',
      'A proposal must change at least one transform.',
      502,
    );
  }

  return {
    id: `proposal_${randomUUID()}`,
    toolName: 'modify_object_transform',
    toolVersion: '1',
    permissionLevel: 'APPROVAL_REQUIRED',
    status: 'awaiting_approval',
    sceneName: scene.scene_name,
    targets: objectIds.map((id) => {
      const object = objectIndex.get(id);
      if (!object)
        throw new AppError('UNKNOWN_OBJECT_ID', 'Target is unavailable.', 502);
      return {
        id,
        name: typeof object.name === 'string' ? object.name : id,
        type: typeof object.type === 'string' ? object.type : 'UNKNOWN',
      };
    }),
    locationDelta,
    rotationDelta,
    scaleMultiplier,
    risk: 'approval_required',
    createdAt: new Date().toISOString(),
  };
};

const validateObjectIds = (value: unknown): string[] => {
  if (
    !Array.isArray(value) ||
    value.length === 0 ||
    value.length > MAX_TARGETS
  ) {
    throw new AppError(
      'INVALID_TOOL_ARGUMENTS',
      `object_ids must contain 1 to ${MAX_TARGETS} IDs.`,
      502,
    );
  }
  if (value.some((item) => typeof item !== 'string' || !item)) {
    throw new AppError(
      'INVALID_TOOL_ARGUMENTS',
      'Each object ID must be a non-empty string.',
      502,
    );
  }
  const objectIds = value as string[];
  if (new Set(objectIds).size !== objectIds.length) {
    throw new AppError(
      'INVALID_TOOL_ARGUMENTS',
      'object_ids must not contain duplicates.',
      502,
    );
  }
  return objectIds;
};

const vector = (
  value: unknown,
  fallback: [number, number, number],
  maximumMagnitude: number,
  field: string,
): [number, number, number] => {
  if (value === undefined) return fallback;
  if (
    !Array.isArray(value) ||
    value.length !== 3 ||
    value.some(
      (item) =>
        typeof item !== 'number' ||
        !Number.isFinite(item) ||
        Math.abs(item) > maximumMagnitude,
    )
  ) {
    throw new AppError(
      'INVALID_TOOL_ARGUMENTS',
      `${field} must contain three bounded numbers.`,
      502,
    );
  }
  return [value[0], value[1], value[2]];
};

const scaleVector = (value: unknown): [number, number, number] => {
  if (value === undefined) return [1, 1, 1];
  if (
    !Array.isArray(value) ||
    value.length !== 3 ||
    value.some(
      (item) =>
        typeof item !== 'number' ||
        !Number.isFinite(item) ||
        item < MIN_SCALE ||
        item > MAX_SCALE,
    )
  ) {
    throw new AppError(
      'INVALID_TOOL_ARGUMENTS',
      'scale_multiplier must contain three values between 0.01 and 100.',
      502,
    );
  }
  return [value[0], value[1], value[2]];
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
