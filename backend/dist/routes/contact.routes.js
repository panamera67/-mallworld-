import { Router } from 'express';
import { randomUUID } from 'node:crypto';
import { z } from 'zod';
import { HttpError } from '../middleware/error-handler.js';
import { logger } from '../utils/logger.js';
const contactSchema = z.object({
    firstName: z.string().trim().min(2).max(50),
    lastName: z.string().trim().min(2).max(50),
    email: z.string().trim().email(),
    company: z.string().trim().min(2).max(100),
    jobTitle: z.string().trim().min(2).max(100),
    monthlyVolume: z.number().positive().finite(),
    message: z.string().trim().min(20).max(2000),
    acceptPrivacyPolicy: z.literal(true)
});
export const contactRouter = Router();
contactRouter.post('/', (req, res, next) => {
    try {
        const payload = contactSchema.parse(req.body);
        const { acceptPrivacyPolicy: _accepted, ...lead } = payload;
        const isDuplicateLead = false;
        if (isDuplicateLead) {
            throw new HttpError('Lead already submitted', 409);
        }
        logger.info({ lead }, 'Inbound enterprise lead captured');
        return res.status(201).json({
            status: 'success',
            data: {
                leadId: randomUUID(),
                message: 'Merci ! Notre équipe vous recontacte sous 24h ouvrées.'
            }
        });
    }
    catch (error) {
        next(error);
    }
});
