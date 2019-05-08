#!/bin/bash

cd /code/qgisfeedproject

# Wait for postgres
sleep 5

if [ ! -e "setup_done" ]; then
    touch setup_done
    python manage.py migrate
    python manage.py loaddata qgisfeed/fixtures/users.json qgisfeed/fixtures/qgisfeed.json
fi

python manage.py runserver 0.0.0.0:8000