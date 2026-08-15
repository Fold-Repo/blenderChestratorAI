import type { ApiErrorResponse } from '@blender-ai/contracts';

export class AppError extends Error {
  public readonly code: string;
  public readonly statusCode: number;
  public readonly details?: unknown;

  constructor(
    code: string,
    message: string,
    statusCode = 500,
    details?: unknown,
  ) {
    super(message);
    this.name = 'AppError';
    this.code = code;
    this.statusCode = statusCode;
    this.details = details;
  }
}

const httpStatus = (error: unknown): number | undefined => {
  if (!error || typeof error !== 'object') {
    return undefined;
  }

  const candidate = error as { status?: unknown; statusCode?: unknown };
  if (typeof candidate.status === 'number') {
    return candidate.status;
  }
  if (typeof candidate.statusCode === 'number') {
    return candidate.statusCode;
  }
  return undefined;
};

export const toApiError = (
  error: unknown,
  requestId: string,
): { statusCode: number; payload: ApiErrorResponse } => {
  if (error instanceof AppError) {
    return {
      statusCode: error.statusCode,
      payload: {
        error: {
          code: error.code,
          message: error.message,
          requestId,
          details: error.details,
        },
      },
    };
  }

  const status = httpStatus(error);
  if (status === 413) {
    return {
      statusCode: 413,
      payload: {
        error: {
          code: 'PAYLOAD_TOO_LARGE',
          message: 'Request body exceeds the 1MB limit.',
          requestId,
        },
      },
    };
  }

  if (status === 400) {
    return {
      statusCode: 400,
      payload: {
        error: {
          code: 'VALIDATION_ERROR',
          message: 'Invalid JSON request body.',
          requestId,
        },
      },
    };
  }

  return {
    statusCode: 500,
    payload: {
      error: {
        code: 'INTERNAL_ERROR',
        message: 'An unexpected error occurred.',
        requestId,
      },
    },
  };
};
