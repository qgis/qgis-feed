#!/bin/bash


LOCKFILE="setup_done.lock"
cd /code/qgisfeedproject

# Wait for postgres
wait-for-it -h postgis -p 5432 -t 60
sleep 10


if [ ! -e ${LOCKFILE} ]; then
    python manage.py migrate
    python manage.py loaddata qgisfeed/fixtures/users.json qgisfeed/fixtures/qgisfeed.json
    touch ${LOCKFILE}

fi

python manage.py runserver 0.0.0.0:8000
