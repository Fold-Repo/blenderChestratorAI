import crypto, { randomUUID } from 'node:crypto';
import express from 'express';
import { SceneAgent } from '../agents/sceneAgent.js';
import { AppError } from '../lib/errors.js';
import {
  createAuditLog,
  createConversation,
  createProject,
  createRun,
  createUsageRecord,
  createUser,
  getConversation,
  getIdempotentRecord,
  getProject,
  getUserByToken,
  getUserByUsername,
  listAuditLogs,
  listProjects,
  listUsageRecords,
  setIdempotentRecord,
} from '../lib/inMemoryStore.js';
import { createSceneProvider } from '../providers/factory.js';

const mutationResponse = (
  req: express.Request,
  res: express.Response,
  statusCode: number,
  payload: unknown,
): { statusCode: number; payload: unknown } => {
  const idempotencyKey = req.header('idempotency-key');
  if (!idempotencyKey) {
    return { statusCode, payload };
  }

  const userId = res.locals.user?.id ?? 'anon';
  const recordKey = `${userId}:${req.method}:${req.path}:${idempotencyKey}`;
  const existing = getIdempotentRecord(recordKey);
  if (existing) {
    return existing;
  }

  setIdempotentRecord(recordKey, statusCode, payload);
  return { statusCode, payload };
};

const toolCallTargetsCount = (result: unknown): number => {
  if (!result || typeof result !== 'object' || !('targets' in result)) {
    return 0;
  }
  const targets = (result as { targets: unknown }).targets;
  return Array.isArray(targets) ? targets.length : 0;
};

const routeParam = (value: string | string[] | undefined): string => {
  if (Array.isArray(value)) {
    return value[0] ?? '';
  }
  return value ?? '';
};

export const createV1Router = () => {
  const router = express.Router();

  // Authentication Middleware
  const requireAuth = (
    req: express.Request,
    res: express.Response,
    next: express.NextFunction,
  ) => {
    const authHeader = req.header('Authorization');
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      next(new AppError('UNAUTHORIZED', 'Authentication required.', 401));
      return;
    }
    const token = authHeader.substring(7).trim();
    const user = getUserByToken(token);
    if (!user) {
      next(new AppError('UNAUTHORIZED', 'Invalid or expired token.', 401));
      return;
    }
    res.locals.user = user;
    next();
  };

  // Auth Routes
  router.post('/auth/register', (req, res) => {
    const username = String(req.body?.username ?? '').trim();
    const email = String(req.body?.email ?? '').trim();
    const password = String(req.body?.password ?? '').trim();
    if (!username || !email || !password) {
      throw new AppError(
        'VALIDATION_ERROR',
        'Username, email, and password are required.',
        400,
      );
    }
    if (getUserByUsername(username)) {
      throw new AppError('CONFLICT', 'Username is already taken.', 409);
    }
    const passwordHash = crypto
      .createHash('sha256')
      .update(password)
      .digest('hex');
    const token = `token_${randomUUID()}`;
    const user = createUser(username, email, passwordHash, token);
    res.status(201).json({
      user: { id: user.id, username: user.username, email: user.email },
      token,
      requestId: res.locals.requestId,
    });
  });

  router.post('/auth/login', (req, res) => {
    const username = String(req.body?.username ?? '').trim();
    const password = String(req.body?.password ?? '').trim();
    if (!username || !password) {
      throw new AppError(
        'VALIDATION_ERROR',
        'Username and password are required.',
        400,
      );
    }
    const user = getUserByUsername(username);
    if (!user) {
      throw new AppError('UNAUTHORIZED', 'Invalid username or password.', 401);
    }
    const passwordHash = crypto
      .createHash('sha256')
      .update(password)
      .digest('hex');
    if (user.passwordHash !== passwordHash) {
      throw new AppError('UNAUTHORIZED', 'Invalid username or password.', 401);
    }
    res.status(200).json({
      user: { id: user.id, username: user.username, email: user.email },
      token: user.token,
      requestId: res.locals.requestId,
    });
  });

  // Health
  router.get('/health', (_req, res) => {
    res.status(200).json({
      status: 'ok',
      service: 'backend',
      version: '0.1.0',
      timestamp: new Date().toISOString(),
      requestId: res.locals.requestId,
    });
  });

  // Project Routes
  router.get('/projects', requireAuth, (_req, res) => {
    res.status(200).json({
      projects: listProjects(res.locals.user.id),
      requestId: res.locals.requestId,
    });
  });

  router.post('/projects', requireAuth, (req, res) => {
    const name = String(req.body?.name ?? '').trim();
    if (!name) {
      throw new AppError('VALIDATION_ERROR', 'Project name is required.', 400);
    }

    const project = createProject(name, res.locals.user.id);
    const payload = {
      project,
      requestId: res.locals.requestId,
    };

    const output = mutationResponse(req, res, 201, payload);
    res.status(output.statusCode).json(output.payload);
  });

  router.get('/projects/:id', requireAuth, (req, res) => {
    const project = getProject(routeParam(req.params.id));
    if (!project || project.ownerId !== res.locals.user.id) {
      throw new AppError('NOT_FOUND', 'Project not found.', 404);
    }

    res.status(200).json({
      project,
      requestId: res.locals.requestId,
    });
  });

  router.post('/projects/:id/conversations', requireAuth, (req, res) => {
    const project = getProject(routeParam(req.params.id));
    if (!project || project.ownerId !== res.locals.user.id) {
      throw new AppError('NOT_FOUND', 'Project not found.', 404);
    }

    const conversation = createConversation(project.id);
    const payload = {
      conversation,
      requestId: res.locals.requestId,
    };

    const output = mutationResponse(req, res, 201, payload);
    res.status(output.statusCode).json(output.payload);
  });

  // Run Route
  router.post(
    '/conversations/:id/runs',
    requireAuth,
    async (req, res, next) => {
      try {
        const conversation = getConversation(routeParam(req.params.id));
        if (!conversation) {
          throw new AppError('NOT_FOUND', 'Conversation not found.', 404);
        }
        const project = getProject(conversation.projectId);
        if (!project || project.ownerId !== res.locals.user.id) {
          throw new AppError('NOT_FOUND', 'Conversation not found.', 404);
        }

        const message = String(req.body?.message ?? '').trim();
        const sceneContext = req.body?.scene_context;
        if (!message) {
          throw new AppError('VALIDATION_ERROR', 'Message is required.', 400);
        }

        const provider = createSceneProvider();
        const agent = new SceneAgent(provider);
        const agentResult = await agent.run(message, sceneContext);
        const run = createRun(
          conversation.id,
          message,
          sceneContext,
          agentResult,
        );

        const isManagedProvider = Boolean(process.env.OPENAI_API_KEY);
        createUsageRecord({
          runId: run.id,
          userId: res.locals.user.id,
          projectId: project.id,
          provider: provider.name,
          model: isManagedProvider
            ? (process.env.OPENAI_MODEL ?? 'gpt-5-mini')
            : provider.name,
          tokenUsage: {
            inputTokens: message.length * 4,
            outputTokens: (agentResult.assistantMessage || '').length * 4,
            totalTokens:
              (message.length + (agentResult.assistantMessage || '').length) *
              4,
          },
          toolCallsCount: agentResult.toolCalls.length,
          estimatedCost: isManagedProvider
            ? 0.002 + agentResult.toolCalls.length * 0.0005
            : 0,
        });

        for (const call of agentResult.toolCalls) {
          const requiresApproval = call.name === 'modify_object_transform';
          createAuditLog({
            userId: res.locals.user.id,
            projectId: project.id,
            action: call.name,
            tool: call.name,
            parametersMetadata: requiresApproval
              ? { targetsCount: toolCallTargetsCount(call.result) }
              : {},
            approvalRequired: requiresApproval,
            approved: !requiresApproval,
            executionResult: requiresApproval ? 'pending_approval' : 'success',
          });
        }

        const payload = {
          run,
          requestId: res.locals.requestId,
        };

        const output = mutationResponse(req, res, 201, payload);
        res.status(output.statusCode).json(output.payload);
      } catch (error) {
        next(error);
      }
    },
  );

  // Usage Route
  router.get('/usage', requireAuth, (_req, res) => {
    res.status(200).json({
      usage: listUsageRecords(res.locals.user.id),
      requestId: res.locals.requestId,
    });
  });

  // Audit Logs Routes
  router.post('/audit-logs', requireAuth, (req, res) => {
    const projectId = String(req.body?.projectId ?? '').trim();
    const action = String(req.body?.action ?? '').trim();
    const tool = req.body?.tool ? String(req.body?.tool) : undefined;
    const parametersMetadata = req.body?.parametersMetadata;
    const approvalRequired = !!req.body?.approvalRequired;
    const approved = !!req.body?.approved;
    const executionResult = req.body?.executionResult
      ? String(req.body?.executionResult)
      : undefined;

    if (!projectId || !action) {
      throw new AppError(
        'VALIDATION_ERROR',
        'projectId and action are required.',
        400,
      );
    }

    const project = getProject(projectId);
    if (!project || project.ownerId !== res.locals.user.id) {
      throw new AppError('NOT_FOUND', 'Project not found.', 404);
    }

    const log = createAuditLog({
      userId: res.locals.user.id,
      projectId,
      action,
      tool,
      parametersMetadata,
      approvalRequired,
      approved,
      executionResult,
    });

    res.status(201).json({
      auditLog: log,
      requestId: res.locals.requestId,
    });
  });

  router.get('/audit-logs', requireAuth, (_req, res) => {
    res.status(200).json({
      auditLogs: listAuditLogs(res.locals.user.id),
      requestId: res.locals.requestId,
    });
  });

  return router;
};
