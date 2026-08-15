import { randomUUID } from 'node:crypto';
import request from 'supertest';
import { describe, expect, it } from 'vitest';
import { createApp } from '../src/app.js';

const registerUser = async (
  app: ReturnType<typeof createApp>,
  username = `user_${randomUUID().slice(0, 8)}`,
) => {
  const response = await request(app)
    .post('/api/v1/auth/register')
    .send({
      username,
      email: `${username}@example.com`,
      password: 'secret-pass',
    });

  expect(response.status).toBe(201);
  return {
    username,
    password: 'secret-pass',
    token: response.body.token as string,
    user: response.body.user as { id: string; username: string; email: string },
    authorization: `Bearer ${response.body.token}`,
  };
};

const createOwnedConversation = async (app: ReturnType<typeof createApp>) => {
  const auth = await registerUser(app);
  const project = await request(app)
    .post('/api/v1/projects')
    .set('Authorization', auth.authorization)
    .send({ name: 'Demo Project' });
  const conversation = await request(app)
    .post(`/api/v1/projects/${project.body.project.id}/conversations`)
    .set('Authorization', auth.authorization)
    .send({});

  return { auth, project, conversation };
};

describe('authentication', () => {
  it('registers a user and returns a session token', async () => {
    const app = createApp();
    const username = `ada_${randomUUID().slice(0, 8)}`;

    const response = await request(app)
      .post('/api/v1/auth/register')
      .send({
        username,
        email: `${username}@example.com`,
        password: 'secret-pass',
      });

    expect(response.status).toBe(201);
    expect(response.body.user.username).toBe(username);
    expect(response.body.token).toMatch(/^token_/);
    expect(response.body.user).not.toHaveProperty('passwordHash');
  });

  it('rejects duplicate usernames', async () => {
    const app = createApp();
    const auth = await registerUser(app);

    const response = await request(app).post('/api/v1/auth/register').send({
      username: auth.username,
      email: 'other@example.com',
      password: 'secret-pass',
    });

    expect(response.status).toBe(409);
    expect(response.body.error.code).toBe('CONFLICT');
  });

  it('logs in with a valid username and password', async () => {
    const app = createApp();
    const auth = await registerUser(app);

    const response = await request(app).post('/api/v1/auth/login').send({
      username: auth.username,
      password: auth.password,
    });

    expect(response.status).toBe(200);
    expect(response.body.token).toBe(auth.token);
  });

  it('rejects invalid credentials', async () => {
    const app = createApp();
    const auth = await registerUser(app);

    const response = await request(app).post('/api/v1/auth/login').send({
      username: auth.username,
      password: 'wrong-password',
    });

    expect(response.status).toBe(401);
    expect(response.body.error.code).toBe('UNAUTHORIZED');
  });

  it('requires username, email, and password on register', async () => {
    const app = createApp();

    const response = await request(app)
      .post('/api/v1/auth/register')
      .send({ username: 'incomplete' });

    expect(response.status).toBe(400);
    expect(response.body.error.code).toBe('VALIDATION_ERROR');
  });
});

describe('v1 API foundation', () => {
  it('creates project, conversation and run', async () => {
    const app = createApp();
    const { auth, conversation } = await createOwnedConversation(app);

    const runResponse = await request(app)
      .post(`/api/v1/conversations/${conversation.body.conversation.id}/runs`)
      .set('Authorization', auth.authorization)
      .send({ message: 'Hello backend' });

    expect(runResponse.status).toBe(201);
    expect(runResponse.body.run.id).toContain('run_');
    expect(runResponse.body.run.assistantMessage).toContain('Hello backend');
  });

  it('returns structured error for invalid mutation payload', async () => {
    const app = createApp();
    const auth = await registerUser(app);

    const response = await request(app)
      .post('/api/v1/projects')
      .set('Authorization', auth.authorization)
      .send({});

    expect(response.status).toBe(400);
    expect(response.body.error.code).toBe('VALIDATION_ERROR');
    expect(response.body.error.requestId).toBeTypeOf('string');
  });

  it('supports idempotency keys for create project', async () => {
    const app = createApp();
    const auth = await registerUser(app);

    const first = await request(app)
      .post('/api/v1/projects')
      .set('Authorization', auth.authorization)
      .set('idempotency-key', 'project-123')
      .send({ name: 'Stable Project' });

    const second = await request(app)
      .post('/api/v1/projects')
      .set('Authorization', auth.authorization)
      .set('idempotency-key', 'project-123')
      .send({ name: 'Stable Project Changed Name' });

    expect(first.status).toBe(201);
    expect(second.status).toBe(201);
    expect(second.body.project.id).toBe(first.body.project.id);
    expect(second.body.project.name).toBe(first.body.project.name);
  });

  it('accepts structured scene context in run requests', async () => {
    const app = createApp();
    const { auth, conversation } = await createOwnedConversation(app);

    const contextPayload = {
      scene: { scene_name: 'Scene', object_count: 3 },
      selection: { selected_object_ids: ['obj:MESH:Cube'] },
    };

    const runResponse = await request(app)
      .post(`/api/v1/conversations/${conversation.body.conversation.id}/runs`)
      .set('Authorization', auth.authorization)
      .send({ message: 'Use context', scene_context: contextPayload });

    expect(runResponse.status).toBe(201);
    expect(runResponse.body.run.sceneContext).toEqual(contextPayload);
  });

  it('runs a natural-language scene inspection through the agent loop', async () => {
    const app = createApp();
    const { auth, conversation } = await createOwnedConversation(app);

    const response = await request(app)
      .post(`/api/v1/conversations/${conversation.body.conversation.id}/runs`)
      .set('Authorization', auth.authorization)
      .send({
        message: 'How many objects are in this scene?',
        scene_context: {
          scene: { scene_name: 'Demo', object_count: 42 },
          selection: { selected_object_ids: [] },
          objects: [],
        },
      });

    expect(response.status).toBe(201);
    expect(response.body.run.assistantMessage).toContain('42 objects');
    expect(response.body.run.toolCalls).toHaveLength(1);
    expect(response.body.run.toolCalls[0].name).toBe('get_scene_summary');
  });
});

describe('project ownership', () => {
  it('requires a bearer token for project mutations', async () => {
    const app = createApp();

    const response = await request(app)
      .post('/api/v1/projects')
      .send({ name: 'Unauthenticated' });

    expect(response.status).toBe(401);
    expect(response.body.error.code).toBe('UNAUTHORIZED');
  });

  it('hides another user project from get, list, and conversation create', async () => {
    const app = createApp();
    const owner = await registerUser(app);
    const stranger = await registerUser(app);

    const project = await request(app)
      .post('/api/v1/projects')
      .set('Authorization', owner.authorization)
      .send({ name: 'Owner Project' });

    const listed = await request(app)
      .get('/api/v1/projects')
      .set('Authorization', stranger.authorization);

    const fetched = await request(app)
      .get(`/api/v1/projects/${project.body.project.id}`)
      .set('Authorization', stranger.authorization);

    const conversation = await request(app)
      .post(`/api/v1/projects/${project.body.project.id}/conversations`)
      .set('Authorization', stranger.authorization)
      .send({});

    expect(listed.status).toBe(200);
    expect(listed.body.projects).toEqual([]);
    expect(fetched.status).toBe(404);
    expect(conversation.status).toBe(404);
  });

  it('does not replay another user idempotent project create', async () => {
    const app = createApp();
    const owner = await registerUser(app);
    const stranger = await registerUser(app);

    const ownerProject = await request(app)
      .post('/api/v1/projects')
      .set('Authorization', owner.authorization)
      .set('idempotency-key', 'shared-key')
      .send({ name: 'Owner Project' });

    const strangerProject = await request(app)
      .post('/api/v1/projects')
      .set('Authorization', stranger.authorization)
      .set('idempotency-key', 'shared-key')
      .send({ name: 'Stranger Project' });

    expect(ownerProject.status).toBe(201);
    expect(strangerProject.status).toBe(201);
    expect(strangerProject.body.project.id).not.toBe(
      ownerProject.body.project.id,
    );
    expect(strangerProject.body.project.ownerId).toBe(stranger.user.id);
  });
});

describe('usage and audit logs', () => {
  it('records usage and tool audit logs when a run executes', async () => {
    const app = createApp();
    const { auth, project, conversation } = await createOwnedConversation(app);

    const runResponse = await request(app)
      .post(`/api/v1/conversations/${conversation.body.conversation.id}/runs`)
      .set('Authorization', auth.authorization)
      .send({
        message: 'How many objects are in this scene?',
        scene_context: {
          scene: { scene_name: 'Demo', object_count: 3 },
          selection: { selected_object_ids: [] },
          objects: [],
        },
      });

    const usage = await request(app)
      .get('/api/v1/usage')
      .set('Authorization', auth.authorization);
    const auditLogs = await request(app)
      .get('/api/v1/audit-logs')
      .set('Authorization', auth.authorization);

    expect(runResponse.status).toBe(201);
    expect(usage.status).toBe(200);
    expect(usage.body.usage).toHaveLength(1);
    expect(usage.body.usage[0].runId).toBe(runResponse.body.run.id);
    expect(usage.body.usage[0].userId).toBe(auth.user.id);
    expect(usage.body.usage[0].projectId).toBe(project.body.project.id);
    expect(usage.body.usage[0].provider).toBe('local-rule-based');
    expect(usage.body.usage[0].toolCallsCount).toBe(1);
    expect(auditLogs.status).toBe(200);
    expect(auditLogs.body.auditLogs[0].action).toBe('get_scene_summary');
  });

  it('creates and lists user-scoped audit logs', async () => {
    const app = createApp();
    const owner = await registerUser(app);
    const stranger = await registerUser(app);
    const project = await request(app)
      .post('/api/v1/projects')
      .set('Authorization', owner.authorization)
      .send({ name: 'Audit Project' });

    const created = await request(app)
      .post('/api/v1/audit-logs')
      .set('Authorization', owner.authorization)
      .send({
        projectId: project.body.project.id,
        action: 'preview',
        tool: 'modify_object_transform',
        parametersMetadata: { targetsCount: 1, password: 'should-hide' },
        approvalRequired: true,
        approved: false,
        executionResult: 'success',
      });

    const ownerLogs = await request(app)
      .get('/api/v1/audit-logs')
      .set('Authorization', owner.authorization);
    const strangerLogs = await request(app)
      .get('/api/v1/audit-logs')
      .set('Authorization', stranger.authorization);
    const strangerWrite = await request(app)
      .post('/api/v1/audit-logs')
      .set('Authorization', stranger.authorization)
      .send({
        projectId: project.body.project.id,
        action: 'apply',
      });

    expect(created.status).toBe(201);
    expect(created.body.auditLog.parametersMetadata.password).toBe(
      '[REDACTED]',
    );
    expect(created.body.auditLog.parametersMetadata.targetsCount).toBe(1);
    expect(ownerLogs.body.auditLogs).toHaveLength(1);
    expect(strangerLogs.body.auditLogs).toEqual([]);
    expect(strangerWrite.status).toBe(404);
  });
});

describe('security controls', () => {
  it('rate limits repeated non-health requests', async () => {
    const app = createApp({ rateLimitMax: 2 });
    const first = await registerUser(app);
    const second = await registerUser(app);
    const third = await request(app)
      .post('/api/v1/auth/register')
      .send({
        username: `user_${randomUUID().slice(0, 8)}`,
        email: 'third@example.com',
        password: 'secret-pass',
      });
    const health = await request(app).get('/health');

    expect(first.token).toMatch(/^token_/);
    expect(second.token).toMatch(/^token_/);
    expect(third.status).toBe(429);
    expect(third.body.error.code).toBe('TOO_MANY_REQUESTS');
    expect(health.status).toBe(200);
  });

  it('rejects JSON bodies larger than 1MB', async () => {
    const app = createApp();
    const oversized = 'x'.repeat(1024 * 1024 + 64);

    const response = await request(app).post('/api/v1/auth/register').send({
      username: 'oversized',
      email: 'oversized@example.com',
      password: oversized,
    });

    expect(response.status).toBe(413);
    expect(response.body.error.code).toBe('PAYLOAD_TOO_LARGE');
  });
});
