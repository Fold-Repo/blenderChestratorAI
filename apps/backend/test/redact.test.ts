import { describe, expect, it, vi } from 'vitest';
import { createLogger } from '../src/lib/logger.js';
import { REDACTED, redactValue } from '../src/lib/redact.js';

describe('secret redaction', () => {
  it('redacts nested credential fields and leaves safe values', () => {
    const redacted = redactValue({
      username: 'ada',
      password: 'secret-pass',
      nested: { apiKey: 'sk-test', token: 'abc', count: 2 },
    }) as Record<string, unknown>;

    expect(redacted.username).toBe('ada');
    expect(redacted.password).toBe(REDACTED);
    expect((redacted.nested as Record<string, unknown>).apiKey).toBe(REDACTED);
    expect((redacted.nested as Record<string, unknown>).token).toBe(REDACTED);
    expect((redacted.nested as Record<string, unknown>).count).toBe(2);
  });

  it('redacts secrets from structured logs', () => {
    const spy = vi.spyOn(console, 'log').mockImplementation(() => undefined);
    const logger = createLogger('test');

    logger.info('login_attempt', {
      username: 'ada',
      password: 'secret-pass',
      authorization: 'Bearer token_abc',
    });

    const logged = JSON.parse(String(spy.mock.calls[0]?.[0]));
    expect(logged.metadata.username).toBe('ada');
    expect(logged.metadata.password).toBe(REDACTED);
    expect(logged.metadata.authorization).toBe(REDACTED);
    spy.mockRestore();
  });
});
