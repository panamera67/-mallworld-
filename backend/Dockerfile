#
# Spectra FX Backend - Production Dockerfile
#

FROM node:18.20-alpine3.19 AS base
WORKDIR /app
ENV NODE_ENV=production

#
# Install dependencies with reproducible npm ci
#
FROM base AS deps
COPY package.json package-lock.json ./
RUN npm ci --omit=dev

#
# Build stage
#
FROM base AS build
ENV NODE_ENV=development
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
RUN npm run build

#
# Production runtime image
#
FROM base AS runtime
USER node
COPY --from=deps /app/node_modules ./node_modules
COPY --from=build /app/dist ./dist
COPY package.json ./
EXPOSE 8080
CMD ["node", "dist/index.js"]
