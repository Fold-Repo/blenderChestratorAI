import { redactValue } from './redact.js';

export type LogLevel = 'debug' | 'info' | 'warn' | 'error';

export interface Logger {
  debug: (message: string, metadata?: Record<string, unknown>) => void;
  info: (message: string, metadata?: Record<string, unknown>) => void;
  warn: (message: string, metadata?: Record<string, unknown>) => void;
  error: (message: string, metadata?: Record<string, unknown>) => void;
}

const print = (
  level: LogLevel,
  message: string,
  metadata?: Record<string, unknown>,
): void => {
  const entry = {
    level,
    message,
    timestamp: new Date().toISOString(),
    ...(metadata
      ? { metadata: redactValue(metadata) as Record<string, unknown> }
      : {}),
  };

  // Structured JSON logs simplify filtering and ingestion in production.
  console.log(JSON.stringify(entry));
};

export const createLogger = (scope: string): Logger => ({
  debug: (message, metadata) => print('debug', message, { scope, ...metadata }),
  info: (message, metadata) => print('info', message, { scope, ...metadata }),
  warn: (message, metadata) => print('warn', message, { scope, ...metadata }),
  error: (message, metadata) => print('error', message, { scope, ...metadata }),
});
