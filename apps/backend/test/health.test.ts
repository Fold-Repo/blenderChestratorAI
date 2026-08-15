import request from 'supertest';
import { describe, expect, it } from 'vitest';
import { createApp } from '../src/app.js';

describe('health endpoint', () => {
  it('returns status payload for /health', async () => {
    const app = createApp();

    const response = await request(app).get('/health');

    expect(response.status).toBe(200);
    expect(response.body.status).toBe('ok');
    expect(response.body.service).toBe('backend');
    expect(response.body.version).toBe('0.1.0');
    expect(response.body.requestId).toBeTypeOf('string');
  });

  it('returns status payload for /api/v1/health', async () => {
    const app = createApp();

    const response = await request(app).get('/api/v1/health');

    expect(response.status).toBe(200);
    expect(response.body.status).toBe('ok');
    expect(response.body.requestId).toBeTypeOf('string');
  });
});
