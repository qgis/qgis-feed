#!/bin/bash

DOCKER_DB=$(docker ps --format '{{.Names}}' | grep qgis-feed_postgis | head -1)
DB_USER=postgres
DB_NAME=qgisfeed
INTERVAL=1

docker exec $DOCKER_DB su - $DB_USER -c "psql -d $DB_NAME -c \"DELETE FROM 
    DJANGO_SESSION WHERE expire_date < now() - interval '$INTERVAL days';\""
