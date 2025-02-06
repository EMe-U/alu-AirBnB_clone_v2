#!/usr/bin/env bash
# This script sets up a web server for deployment of web_static

if ! dpkg -s nginx &> /dev/null; then
    apt-get update
    apt-get install -y nginx
fi

mkdir -p /data/web_static/releases/test /data/web_static/shared

echo -e "<html>\n  <head>\n  </head>\n  <body>\n    Holberton School\n  </body>\n</html>" > /data/web_static/releases/test/index.html

ln -sfn /data/web_static/releases/test/ /data/web_static/current

chown -R ubuntu:ubuntu /data/

NGINX_CONF="/etc/nginx/sites-available/default"
if ! grep -q "location /hbnb_static/" $NGINX_CONF; then
    sed -i "/server_name _;/a \\ 
    location /hbnb_static/ {\\n\\talias /data/web_static/current/;\\n\\t}" $NGINX_CONF
fi

service nginx restart

exit 0
