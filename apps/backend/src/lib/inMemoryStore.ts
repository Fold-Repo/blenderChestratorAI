import { randomUUID } from 'node:crypto';
import { redactValue } from './redact.js';

export interface User {
  id: string;
  username: string;
  email: string;
  passwordHash: string;
  token: string;
  createdAt: string;
}

export interface Project {
  id: string;
  name: string;
  ownerId: string;
  createdAt: string;
}

export interface Conversation {
  id: string;
  projectId: string;
  createdAt: string;
}

export interface Run {
  id: string;
  conversationId: string;
  userMessage: string;
  assistantMessage: string;
  sceneContext?: unknown;
  status: 'completed' | 'waiting_for_approval' | 'failed' | 'cancelled';
  toolCalls: Array<{ name: string; result: unknown }>;
  agentStateHistory: string[];
  proposal?: unknown;
  createdAt: string;
}

export interface UsageRecord {
  id: string;
  runId: string;
  userId: string;
  projectId: string;
  provider: string;
  model: string;
  tokenUsage?: {
    inputTokens: number;
    outputTokens: number;
    totalTokens: number;
  };
  toolCallsCount: number;
  estimatedCost: number;
  createdAt: string;
}

export interface AuditLog {
  id: string;
  userId: string;
  projectId: string;
  action: string;
  tool?: string;
  parametersMetadata?: unknown;
  approvalRequired: boolean;
  approved: boolean;
  executionResult?: string;
  timestamp: string;
}

interface IdempotentRecord {
  statusCode: number;
  payload: unknown;
}

const users = new Map<string, User>();
const projects = new Map<string, Project>();
const conversations = new Map<string, Conversation>();
const runs = new Map<string, Run>();
const usageRecords = new Map<string, UsageRecord>();
const auditLogs = new Map<string, AuditLog>();
const idempotencyRecords = new Map<string, IdempotentRecord>();

const now = () => new Date().toISOString();

export const createUser = (
  username: string,
  email: string,
  passwordHash: string,
  token: string,
): User => {
  const user: User = {
    id: `user_${randomUUID()}`,
    username,
    email,
    passwordHash,
    token,
    createdAt: now(),
  };
  users.set(user.id, user);
  return user;
};

export const getUserByToken = (token: string): User | undefined => {
  for (const user of users.values()) {
    if (user.token === token) return user;
  }
  return undefined;
};

export const getUserByUsername = (username: string): User | undefined => {
  for (const user of users.values()) {
    if (user.username.toLowerCase() === username.toLowerCase()) return user;
  }
  return undefined;
};

export const listProjects = (ownerId?: string): Project[] => {
  const all = [...projects.values()];
  if (ownerId) return all.filter((p) => p.ownerId === ownerId);
  return all;
};

export const createProject = (name: string, ownerId: string): Project => {
  const project: Project = {
    id: `proj_${randomUUID()}`,
    name,
    ownerId,
    createdAt: now(),
  };

  projects.set(project.id, project);
  return project;
};

export const getProject = (projectId: string): Project | undefined =>
  projects.get(projectId);

export const createConversation = (projectId: string): Conversation => {
  const conversation: Conversation = {
    id: `conv_${randomUUID()}`,
    projectId,
    createdAt: now(),
  };

  conversations.set(conversation.id, conversation);
  return conversation;
};

export const getConversation = (
  conversationId: string,
): Conversation | undefined => conversations.get(conversationId);

export const createRun = (
  conversationId: string,
  userMessage: string,
  sceneContext?: unknown,
  agentResult?: Pick<
    Run,
    'assistantMessage' | 'status' | 'toolCalls' | 'proposal'
  > & {
    stateHistory: string[];
  },
): Run => {
  const run: Run = {
    id: `run_${randomUUID()}`,
    conversationId,
    userMessage,
    assistantMessage:
      agentResult?.assistantMessage ?? `Backend response: ${userMessage}`,
    sceneContext,
    status: agentResult?.status ?? 'completed',
    toolCalls: agentResult?.toolCalls ?? [],
    agentStateHistory: agentResult?.stateHistory ?? ['queued', 'completed'],
    proposal: agentResult?.proposal,
    createdAt: now(),
  };

  runs.set(run.id, run);
  return run;
};

export const createUsageRecord = (
  record: Omit<UsageRecord, 'id' | 'createdAt'>,
): UsageRecord => {
  const usage: UsageRecord = {
    id: `usage_${randomUUID()}`,
    ...record,
    createdAt: now(),
  };
  usageRecords.set(usage.id, usage);
  return usage;
};

export const createAuditLog = (
  log: Omit<AuditLog, 'id' | 'timestamp'>,
): AuditLog => {
  const audit: AuditLog = {
    id: `audit_${randomUUID()}`,
    ...log,
    parametersMetadata: redactValue(log.parametersMetadata),
    timestamp: now(),
  };
  auditLogs.set(audit.id, audit);
  return audit;
};

export const listUsageRecords = (userId: string): UsageRecord[] =>
  [...usageRecords.values()].filter((record) => record.userId === userId);

export const listAuditLogs = (userId: string): AuditLog[] =>
  [...auditLogs.values()].filter((log) => log.userId === userId);

export const getIdempotentRecord = (
  key: string,
): IdempotentRecord | undefined => idempotencyRecords.get(key);

export const setIdempotentRecord = (
  key: string,
  statusCode: number,
  payload: unknown,
): void => {
  idempotencyRecords.set(key, {
    statusCode,
    payload,
  });
};
