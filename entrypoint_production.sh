#!/bin/bash

# Input:
#       - QGIS_FEED_PRODUCTION default false, if true
#         the app will be configured for production
#       - QGIS_FEED_PERSISTENT_STORAGE default ".", a persistent shared volume
#         for data, lockfiles etc.


PRODUCTION=${QGIS_FEED_PRODUCTION:-false}
PERSISTENT_STORAGE=${QGIS_FEED_PERSISTENT_STORAGE:-""}
LOCKFILE="${PERSISTENT_STORAGE}/setup_done.lock"
cd /code/qgisfeedproject

# Wait for postgres
wait-for-it -h postgis -p 5432 -t 60
sleep 10


if [ ! -e ${LOCKFILE} ]; then
    python manage.py migrate
    python manage.py loaddata qgisfeed/fixtures/users.json qgisfeed/fixtures/qgisfeed.json
    touch ${LOCKFILE}
    if [ ${PRODUCTION} ]; then
        python manage.py collectstatic --noinput
    fi
fi

if [ ${PRODUCTION} ]; then
    gunicorn base.wsgi:application --error-logfile - --timeout 120 --workers=4 -b 0.0.0.0:8000
else
    python manage.py runserver 0.0.0.0:8000
fi