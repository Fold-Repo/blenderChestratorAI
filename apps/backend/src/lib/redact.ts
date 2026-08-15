const SENSITIVE_KEY =
  /^(password|passwd|token|access_token|refresh_token|authorization|api[_-]?key|secret|credential|auth[_-]?token|cookie)$/i;

export const REDACTED = '[REDACTED]';

export const redactValue = (value: unknown): unknown => {
  if (Array.isArray(value)) {
    return value.map(redactValue);
  }

  if (value && typeof value === 'object') {
    return Object.fromEntries(
      Object.entries(value as Record<string, unknown>).map(([key, nested]) => [
        key,
        SENSITIVE_KEY.test(key) ? REDACTED : redactValue(nested),
      ]),
    );
  }

  return value;
};
