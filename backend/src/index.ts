import { createServer } from 'node:http';
import { config } from './config.js';
import { createApp } from './app.js';
import { logger } from './utils/logger.js';

const app = createApp();
const server = createServer(app);

const onShutdown = (signal: NodeJS.Signals) => {
  logger.info({ signal }, 'Shutdown signal received');
  server.close((error) => {
    if (error) {
      logger.error({ error }, 'Error during graceful shutdown');
      process.exit(1);
    }
    logger.info('HTTP server closed gracefully');
    process.exit(0);
  });
};

process.on('SIGINT', onShutdown);
process.on('SIGTERM', onShutdown);

server.listen(config.port, () => {
  logger.info(
    { port: config.port, environment: config.nodeEnv },
    'Spectra FX backend API listening'
  );
});