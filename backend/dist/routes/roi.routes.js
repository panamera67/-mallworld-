import { Router } from 'express';
import { z } from 'zod';
import { config } from '../config.js';
const roiSchema = z.object({
    volume: z.number().positive().finite(),
    spread: z.number().positive().finite(),
    optimization: z
        .number()
        .positive()
        .max(0.1, 'Optimization cannot exceed 10% without manual approval') // guardrail
});
const formatCurrency = (value) => new Intl.NumberFormat('fr-FR', {
    style: 'currency',
    currency: 'EUR',
    maximumFractionDigits: 0
}).format(value);
export const roiRouter = Router();
roiRouter.post('/', (req, res, next) => {
    try {
        const { volume, spread, optimization } = roiSchema.parse(req.body);
        const spreadReduction = spread * optimization;
        const monthlySaving = volume * spreadReduction;
        const annualSaving = monthlySaving * 12;
        const roiMultiple = annualSaving / config.roiSubscriptionCost;
        return res.status(200).json({
            status: 'success',
            data: {
                monthlySaving,
                annualSaving,
                roiMultiple,
                formatted: {
                    monthlySaving: formatCurrency(monthlySaving),
                    annualSaving: formatCurrency(annualSaving),
                    roiMultiple: `${roiMultiple.toFixed(1)}x`
                }
            }
        });
    }
    catch (error) {
        next(error);
    }
});
