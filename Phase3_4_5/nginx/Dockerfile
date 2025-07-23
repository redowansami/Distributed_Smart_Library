FROM nginx:alpine

RUN rm /etc/nginx/conf.d/default.conf

COPY nginx.conf /etc/nginx/nginx.conf

RUN mkdir -p /var/log/nginx && \
    mkdir -p /var/cache/nginx && \
    touch /var/run/nginx.pid && \
    chown -R nginx:nginx /var/log/nginx /var/cache/nginx /var/run/nginx.pid

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
