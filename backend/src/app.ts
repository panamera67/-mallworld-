import express, { type Express } from 'express';
import helmet from 'helmet';
import pinoHttp from 'pino-http';
import { apiRouter } from './routes/index.js';
import { errorHandler } from './middleware/error-handler.js';
import { logger } from './utils/logger.js';

export const createApp = (): Express => {
  const app = express();

  app.disable('x-powered-by');
  app.use(helmet());
  app.use(express.json({ limit: '100kb' }));
  app.use(express.urlencoded({ extended: true }));

  app.use(
    pinoHttp({
      logger,
      autoLogging: true,
      redact: ['req.headers.authorization', 'req.headers.cookie']
    })
  );

  app.get('/health', (_req, res) => {
    res.status(200).json({
      status: 'ok',
      uptime: process.uptime()
    });
  });

  app.use('/api/v1', apiRouter);

  app.use((_req, res) => {
    res.status(404).json({
      status: 'error',
      message: 'Route not found'
    });
  });

  app.use(errorHandler);

  return app;
};