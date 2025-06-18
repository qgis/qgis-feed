CONTAINER_NAME := qgisfeed
SHELL := /usr/bin/env bash

# ----------------------------------------------------------------------------
#    D E V E L O P M E N T    C O M M A N D S
# ----------------------------------------------------------------------------
default: dev-build
run: dev-build dev-start

dev-build:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Building in development mode"
	@echo "------------------------------------------------------------------"
	@docker compose -f docker-compose.dev.yml build

dev-start:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Running in development mode"
	@echo "------------------------------------------------------------------"
	@docker-compose -f docker-compose.dev.yml up

dev-logs:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Show the logs in development mode"
	@echo "------------------------------------------------------------------"
	@docker logs -f $(CONTAINER_NAME)

dev-update-migrations:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Running makemigrations in development mode"
	@echo "------------------------------------------------------------------"
	@docker compose -f docker-compose.dev.yml exec $(CONTAINER_NAME) python qgisfeedproject/manage.py makemigrations

dev-migrate:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Running migrate in development mode"
	@echo "------------------------------------------------------------------"
	@docker compose -f docker-compose.dev.yml exec $(CONTAINER_NAME) python qgisfeedproject/manage.py migrate

dev-dbseed:
	@echom
	@echo "------------------------------------------------------------------"
	@echo "Seed db with JSON data from /fixtures/*.json"
	@echo "------------------------------------------------------------------"
	@docker compose -f docker-compose.dev.yml exec $(CONTAINER_NAME) python qgisfeedproject/manage.py loaddata qgisfeedproject/qgisfeed/fixtures/*.json


dev-dbrestore:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Restore dump from /backups/latest-qgisfeed.dmp and  /backups/latest-metabase.dmp in production mode"
	@echo "------------------------------------------------------------------"
	@echo "stopping qgisfeed container"
	@docker compose -f docker-compose.dev.yml stop qgisfeed
	@echo "Dropping the gis and metabase databases"
	-@docker compose -f docker-compose.dev.yml exec postgis su - postgres -c "dropdb --force qgisfeed"
	-@docker compose -f docker-compose.dev.yml exec postgis su - postgres -c "dropdb --force metabase"
	@echo "Creating the qgisfeed and metabase databases"
	-@docker compose -f docker-compose.dev.yml exec postgis su - postgres -c "createdb -O docker -T template1 qgisfeed"
	-@docker compose -f docker-compose.dev.yml exec postgis su - postgres -c "createdb -O docker -T template1 metabase"
	@echo "Restore database from backups/latest-qgisfeed.dmp and backups/latest-metabase.dmp"
	@docker compose -f docker-compose.dev.yml exec postgis su - postgres -c "pg_restore -c /backups/latest-qgisfeed.dmp -d qgisfeed"
	@docker compose -f docker-compose.dev.yml exec postgis su - postgres -c "pg_restore -c /backups/latest-metabase.dmp -d metabase"
	@echo "Starting qgisfeed container"
	@docker compose -f docker-compose.dev.yml up qgisfeed

dev-exportusers:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Create an admin user"
	@echo "------------------------------------------------------------------"
	@docker compose -f docker-compose.dev.yml exec $(CONTAINER_NAME) python qgisfeedproject/manage.py export_users_to_keycloak --realm $(r) --output $(o)

dev-createsuperuser:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Create an admin user"
	@echo "------------------------------------------------------------------"
	@docker compose -f docker-compose.dev.yml exec $(CONTAINER_NAME) python qgisfeedproject/manage.py createsuperuser

dev-runtests:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Running tests in development mode"
	@echo "------------------------------------------------------------------"
	@docker compose -f docker-compose.dev.yml exec $(CONTAINER_NAME) python qgisfeedproject/manage.py test qgisfeed

dev-stop:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Stopping the development server"
	@echo "------------------------------------------------------------------"
	@docker compose -f docker-compose.dev.yml down

# ----------------------------------------------------------------------------
#    P R O D U C T I O N    C O M M A N D S
# ----------------------------------------------------------------------------

build:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Building in production mode"
	@echo "------------------------------------------------------------------"
	@docker compose -f docker-compose-production-ssl.yml build

start:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Starting all or specific container(s) in production mode."
	@echo "------------------------------------------------------------------"
	@docker compose -f docker-compose-production-ssl.yml up -d $(c)

restart:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Restarting all or specific container(s) in production mode."
	@echo "------------------------------------------------------------------"
	@docker compose -f docker-compose-production-ssl.yml up -d $(c)

kill:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Killing all or a specific container(s) in production mode"
	@echo "------------------------------------------------------------------"
	@docker compose -f docker-compose-production-ssl.yml kill $(c)

dbrestore:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Restore dump from /backups/latest-qgisfeed.dmp and  /backups/latest-metabase.dmp in production mode"
	@echo "------------------------------------------------------------------"
	@echo "stopping qgisfeed container"
	@docker compose -f docker-compose-production-ssl.yml stop qgisfeed
	@echo "Dropping the gis and metabase databases"
	-@docker compose -f docker-compose-production-ssl.yml exec postgis su - postgres -c "dropdb --force qgisfeed"
	-@docker compose -f docker-compose-production-ssl.yml exec postgis su - postgres -c "dropdb --force metabase"
	@echo "Creating the qgisfeed and metabase databases"
	-@docker compose -f docker-compose-production-ssl.yml exec postgis su - postgres -c "createdb -O docker -T template1 qgisfeed"
	-@docker compose -f docker-compose-production-ssl.yml exec postgis su - postgres -c "createdb -O docker -T template1 metabase"
	@echo "Restore database from backups/latest-qgisfeed.dmp and backups/latest-metabase.dmp"
	@docker compose -f docker-compose-production-ssl.yml exec postgis su - postgres -c "pg_restore -c /backups/latest-qgisfeed.dmp -d qgisfeed"
	@docker compose -f docker-compose-production-ssl.yml exec postgis su - postgres -c "pg_restore -c /backups/latest-metabase.dmp -d metabase"
	@echo "Starting qgisfeed container"
	@docker compose -f docker-compose-production-ssl.yml up -d qgisfeed

updatemigrations:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Running in production mode"
	@echo "------------------------------------------------------------------"
	@docker compose -f docker-compose-production-ssl.yml exec $(CONTAINER_NAME) python qgisfeedproject/manage.py makemigrations

migrate:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Running migrate in production mode"
	@echo "------------------------------------------------------------------"
	@docker compose -f docker-compose-production-ssl.yml exec $(CONTAINER_NAME) python qgisfeedproject/manage.py migrate

createsuperuser:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Create an admin user"
	@echo "------------------------------------------------------------------"
	@docker compose -f docker-compose-production-ssl.yml exec $(CONTAINER_NAME) python qgisfeedproject/manage.py createsuperuser

collectstatic:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Collecting static in production mode"
	@echo "------------------------------------------------------------------"
	@docker compose -f docker-compose-production-ssl.yml exec $(CONTAINER_NAME) python qgisfeedproject/manage.py collectstatic --noinput


get-sustaining-members:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Getting sustaining members section"
	@echo "------------------------------------------------------------------"
	@docker compose -f docker-compose-production-ssl.yml exec $(CONTAINER_NAME) python qgisfeedproject/manage.py get_sustaining_members


qgisfeed-shell:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Shelling into the qgisfeed container"
	@echo "------------------------------------------------------------------"
	@docker compose -f docker-compose-production-ssl.yml exec qgisfeed bash

qgisfeed-logs:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Show the qgisfeed container logs"
	@echo "------------------------------------------------------------------"
	@docker compose -f docker-compose-production-ssl.yml logs -f qgisfeed

nginx-shell:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Shelling into the nginx container"
	@echo "------------------------------------------------------------------"
	@docker compose -f docker-compose-production-ssl.yml exec nginx bash

nginx-logs:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Show the nginx container logs"
	@echo "------------------------------------------------------------------"
	@docker compose -f docker-compose-production-ssl.yml logs -f nginx

logs:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Tailing all logs or a specific container"
	@echo "------------------------------------------------------------------"
	@docker compose -f docker-compose-production-ssl.yml logs -f $(c)

shell:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Shelling into a specific container"
	@echo "------------------------------------------------------------------"
	@docker compose -f docker-compose-production-ssl.yml exec $(c) bash

exec:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Execute a specific docker command"
	@echo "------------------------------------------------------------------"
	@docker compose -f docker-compose-production-ssl.yml $(c)

exportusers:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Create an admin user"
	@echo "------------------------------------------------------------------"
	@docker compose -f docker-compose-production-ssl.yml exec $(CONTAINER_NAME) python qgisfeedproject/manage.py export_users_to_keycloak --realm $(r) --output $(o)
