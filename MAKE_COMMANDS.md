# Docker compose commands Documentation

## Overview
This doc is designed for managing the Docker-based project. It includes various commands for building, running, and maintaining both production and development environments. Below is a detailed description of each command available in the Makefile.

## Commands

### Production Commands

- **build**: Builds Docker images for both production environment.
```sh
make build
```

- **start**: Starts a specific container or all containers. Specify the container with the `c` variable.
```sh
make start c=container_name
```

- **restart**: Restart a specific container or all containers. Specify the container with the `c` variable.
```sh
make restart c=container_name
```

- **kill**: Stops a specific container or all containers. Specify the container with the `c` variable.
```sh
make kill c=container_name
```

- **dbrestore:** Restores the database from a backup file.
```sh
make dbrestore
```

- **update-migrations**: Creates new migration files based on changes in models.
```sh
make update-migrations
```

- **migrate**: Runs database migrations, with the `auth` app being migrated first.
```sh
make migrate
```

- **createsuperuser**: Create an admin user.
```sh
make createsuperuser
```

- **qgisfeed-shell:** Opens a shell in the `qgisfeed` container.
```sh
make qgisfeed-shell
```

- **qgisfeed-logs:** Tails the requests logs in the `qgisfeed` container.
```sh
make qgisfeed-logs
```

- **nginx-shell:** Opens a shell in the `nginx` container.
```sh
make nginx-shell
```

- **nginx-logs:** Tails the requests logs in the `nginx` container.
```sh
make nginx-logs
```

- **logs:** Tails logs for a specific container or all containers. Specify the container with the `c` variable.
```sh
make logs c=container_name
```

- **shell:** Opens a shell in a specific container. Specify the container with the `c` variable.
```sh
make shell c=container_name
```

- **exec:** Executes a specific Docker command. Specify the command with the `c` variable.
```sh
make exec c="command"
```

#### Development Commands

- **dev-build:** Builds Docker images for the development environment.
```sh
make dev-build
```

- **dev-start:** Start all containers in development environment.
```sh
make dev-start
```

- **dev-logs:** Show the logs in development mode.
```sh
make dev-logs
```

- **dev-update-migrations**: Creates new migration files based on changes in models.
```sh
make dev-update-migrations
```

- **dev-migrate**: Runs database migrations, with the `auth` app being migrated first.
```sh
make dev-migrate
```

- **dev-dbseed**: Seed db with JSON data from /fixtures/*.json.
```sh
make dev-dbseed
```

- **dev-createsuperuser**: Create an admin user.
```sh
make dev-createsuperuser
```

- **dev-runtests**: Running tests in development mode.
```sh
make dev-runtests
```

- **dev-stop**: Stopping the development server.
```sh
make dev-stop
```