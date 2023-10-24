#!/bin/bash


LOCKFILE="setup_done.lock"

# Install Bulma CSS dependencies and build the bundle
npm install && npm run build

cd /code/qgisfeedproject

# Wait for postgres
wait-for-it -h postgis -p 5432 -t 60
sleep 10


python manage.py migrate

if [ ! -e ${LOCKFILE} ]; then
    python manage.py loaddata qgisfeed/fixtures/users.json qgisfeed/fixtures/qgisfeed.json
    touch ${LOCKFILE}

fi

python manage.py runserver 0.0.0.0:8000
