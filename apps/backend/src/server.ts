import { createApp } from './app.js';
import { createLogger } from './lib/logger.js';

const logger = createLogger('server');
const app = createApp();

const port = Number(process.env.PORT ?? 3009);

app.listen(port, () => {
  logger.info('backend_started', {
    port,
    healthEndpoint: '/health',
    versionedHealthEndpoint: '/api/v1/health',
  });
});
