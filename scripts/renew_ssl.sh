#!/bin/bash

/usr/local/bin/docker-compose -f /home/web/qgis-feed/docker-compose-production-ssl.yml run certbot renew --dry-run \
&& /usr/local/bin/docker-compose -f /home/web/qgis-feed/docker-compose-production-ssl.yml kill -s SIGHUP nginx
