# /hakkinda ve /og.png'yi sunan nginx (docker-compose.yaml'daki statik servisi).
FROM nginx:1.29-alpine
COPY deploy/statik/nginx.conf /etc/nginx/conf.d/default.conf
COPY static/hakkinda.html static/og.png /usr/share/nginx/html/
