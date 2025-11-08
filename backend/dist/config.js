import 'dotenv/config';
const parseNumber = (value, fallback) => {
    if (!value) {
        return fallback;
    }
    const parsed = Number(value);
    if (Number.isNaN(parsed) || parsed <= 0) {
        return fallback;
    }
    return parsed;
};
export const config = {
    port: parseNumber(process.env.PORT, 8080),
    nodeEnv: process.env.NODE_ENV ?? 'development',
    roiSubscriptionCost: parseNumber(process.env.ROI_SUBSCRIPTION_COST, 299 * 12)
};
export const isProduction = config.nodeEnv === 'production';
