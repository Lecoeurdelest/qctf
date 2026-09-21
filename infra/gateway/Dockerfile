FROM node:24-alpine AS web
WORKDIR /app
COPY apps/web/package.json apps/web/package-lock.json ./
RUN npm ci
COPY apps/web/ ./
RUN npm run build

FROM nginx:1.28-alpine
COPY infra/gateway/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=web /app/dist /usr/share/nginx/html
EXPOSE 8080

