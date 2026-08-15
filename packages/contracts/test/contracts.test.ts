import { describe, expect, it } from 'vitest';
import type {
  AuditLog,
  AuthResponse,
  HealthResponse,
  UsageRecord,
} from '../src/index.js';

describe('contracts', () => {
  it('defines health response shape', () => {
    const payload: HealthResponse = {
      status: 'ok',
      service: 'backend',
      version: '0.1.0',
      timestamp: new Date().toISOString(),
      requestId: 'req-123',
    };

    expect(payload.status).toBe('ok');
    expect(payload.service).toBeTypeOf('string');
  });

  it('defines auth, usage, and audit response shapes', () => {
    const auth: AuthResponse = {
      user: { id: 'user_1', username: 'ada', email: 'ada@example.com' },
      token: 'token_1',
      requestId: 'req-123',
    };
    const usage: UsageRecord = {
      id: 'usage_1',
      runId: 'run_1',
      userId: 'user_1',
      projectId: 'proj_1',
      provider: 'local-rule-based',
      model: 'local-rule-based',
      toolCallsCount: 1,
      estimatedCost: 0,
      createdAt: new Date().toISOString(),
    };
    const audit: AuditLog = {
      id: 'audit_1',
      userId: 'user_1',
      projectId: 'proj_1',
      action: 'preview',
      approvalRequired: true,
      approved: false,
      timestamp: new Date().toISOString(),
    };

    expect(auth.user.username).toBe('ada');
    expect(usage.provider).toBe('local-rule-based');
    expect(audit.action).toBe('preview');
  });
});
