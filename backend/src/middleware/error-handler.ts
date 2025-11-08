import type { ErrorRequestHandler } from 'express';
import { ZodError } from 'zod';
import { logger } from '../utils/logger.js';

export class HttpError extends Error {
  constructor(
    message: string,
    public readonly statusCode: number = 500,
    public readonly details?: Record<string, unknown>
  ) {
    super(message);
  }
}

export const errorHandler: ErrorRequestHandler = (err, _req, res, _next) => {
  if (err instanceof ZodError) {
    logger.warn({ err }, 'Invalid request payload');
    const formatted = err.errors.map((issue) => ({
      path: issue.path.join('.'),
      message: issue.message
    }));
    return res.status(400).json({
      status: 'error',
      message: 'Invalid request payload',
      errors: formatted
    });
  }

  const status = err instanceof HttpError ? err.statusCode : 500;

  if (status >= 500) {
    logger.error({ err }, 'Unexpected server error');
  } else {
    logger.warn({ err }, 'Handled error');
  }

  const responseBody = {
    status: 'error',
    message: err instanceof HttpError ? err.message : 'Internal server error',
    ...(err instanceof HttpError && err.details ? { details: err.details } : {})
  };

  return res.status(status).json(responseBody);
};
