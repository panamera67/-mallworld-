import { Router } from 'express';
import { contactRouter } from './contact.routes.js';
import { roiRouter } from './roi.routes.js';

export const apiRouter = Router();

apiRouter.use('/roi', roiRouter);
apiRouter.use('/contact', contactRouter);
