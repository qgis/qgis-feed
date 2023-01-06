#!/bin/bash

crontab -l > remove_django_session_cronjob

echo "0 0 * * * sh ${PWD}/remove_old_django_session.sh" >> remove_django_session_cronjob

crontab remove_django_session_cronjob

rm remove_django_session_cronjob
