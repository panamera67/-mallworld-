FROM node:18-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN npm install --silent

COPY . .
RUN npm run build

FROM nginx:alpine AS runtime

COPY nginx.conf /etc/nginx/nginx.conf
COPY --from=builder /app/dist /usr/share/nginx/html

EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s \
    CMD curl -f http://localhost:3000 || exit 1

CMD ["nginx", "-g", "daemon off;"]
