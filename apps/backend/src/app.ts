import { randomUUID } from 'node:crypto';
import type { HealthResponse } from '@blender-ai/contracts';
import express from 'express';
import { AppError, toApiError } from './lib/errors.js';
import { createLogger } from './lib/logger.js';
import { createV1Router } from './routes/v1.js';

const logger = createLogger('app');

export interface CreateAppOptions {
  rateLimitMax?: number;
  rateLimitWindowMs?: number;
}

const healthPayload = (requestId: string): HealthResponse => ({
  status: 'ok',
  service: 'backend',
  version: '0.1.0',
  timestamp: new Date().toISOString(),
  requestId,
});

export const createApp = (options: CreateAppOptions = {}) => {
  const app = express();
  const rateLimits = new Map<string, { count: number; resetTime: number }>();
  const rateLimitWindowMs = options.rateLimitWindowMs ?? 60 * 1000;
  const rateLimitMax = options.rateLimitMax ?? 100;

  const rateLimiter = (
    req: express.Request,
    res: express.Response,
    next: express.NextFunction,
  ) => {
    if (req.path === '/health' || req.path === '/api/v1/health') {
      next();
      return;
    }

    const ip = req.ip || 'unknown';
    const now = Date.now();
    const limit = rateLimits.get(ip);

    if (!limit || now > limit.resetTime) {
      rateLimits.set(ip, { count: 1, resetTime: now + rateLimitWindowMs });
      next();
      return;
    }

    if (limit.count >= rateLimitMax) {
      res.setHeader('Retry-After', Math.ceil((limit.resetTime - now) / 1000));
      next(
        new AppError(
          'TOO_MANY_REQUESTS',
          'Rate limit exceeded. Please try again later.',
          429,
        ),
      );
      return;
    }

    limit.count += 1;
    next();
  };

  // Guard against oversized requests (max 1MB).
  app.use(express.json({ limit: '1mb' }));

  app.use((req, res, next) => {
    const requestId = req.header('x-request-id') ?? randomUUID();
    res.setHeader('x-request-id', requestId);
    res.locals.requestId = requestId;
    next();
  });

  app.use(rateLimiter);

  app.get('/health', (_req, res) => {
    res.status(200).json(healthPayload(res.locals.requestId as string));
  });

  app.get('/api/v1/health', (_req, res) => {
    res.status(200).json(healthPayload(res.locals.requestId as string));
  });

  app.use('/api/v1', createV1Router());

  app.use((_req, _res, next) => {
    next(new AppError('NOT_FOUND', 'Route not found.', 404));
  });

  app.use(
    (
      error: unknown,
      _req: express.Request,
      res: express.Response,
      _next: express.NextFunction,
    ) => {
      const requestId = (res.locals.requestId as string) ?? randomUUID();
      const apiError = toApiError(error, requestId);

      logger.error('request_failed', {
        requestId,
        statusCode: apiError.statusCode,
        error: apiError.payload.error.code,
      });

      res.status(apiError.statusCode).json(apiError.payload);
    },
  );

  return app;
};
