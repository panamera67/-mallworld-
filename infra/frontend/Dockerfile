FROM nginx:1.27-alpine
WORKDIR /usr/share/nginx/html
RUN rm -rf ./*
COPY ./index.html ./index.html
COPY infra/frontend/nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
