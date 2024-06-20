# Fyle QBO API
Django Rest Framework API for Fyle Quickbooks Online Integration


### Setup

* Add and update the `fyle_integrations_imports` submodule
    ```bash
    $ git submodule init
    $ git submodule update
    ```

* Download and install Docker desktop for Mac from [here.](https://www.docker.com/products/docker-desktop)

* If you're using a linux machine, please download docker according to the distrubution you're on.

* Copy docker-compose.yml.template as docker-compose.yml and add required secrets

    ```
    $ cp docker-compose.yml.template docker-compose.yml
    ```

* Setup environment variables in docker_compose.yml

    ```yaml
    environment:
      SECRET_KEY: thisisthedjangosecretkey
      ALLOWED_HOSTS: "*"
      DEBUG: "False"
      API_URL: http://localhost:8000/api
      DATABASE_URL: postgres://postgres:postgres@db:5432/qbo_db
      FYLE_BASE_URL:
      FYLE_CLIENT_ID:
      FYLE_CLIENT_SECRET:
      FYLE_TOKEN_URI:
      QBO_CLIENT_ID:
      QBO_CLIENT_SECRET:
      QBO_REDIRECT_URI:
      QBO_TOKEN_URI:
      QBO_ENVIRONMENT:
   ```

* Build docker images

    ```
    docker-compose build api qcluster
    ```

* Run docker containers

    ```
    docker-compose up -d db api qcluster
    ```

* The database can be accessed by this command, on password prompt type `postgres`

    ```
    docker-compose run -e PGPASSWORD=postgres db psql -h db -U postgres qbo_db
    ```

* To tail the logs of a service you can do

    ```
    docker-compose logs -f <api / qcluster>
    ```

* To stop the containers

    ```
    docker-compose stop api qcluster
    ```

* To restart any containers - `would usually be needed with qcluster after you make any code changes`

    ```
    docker-compose restart qcluster
    ```

* To run bash inside any container for purpose of debugging do

    ```
    docker-compose exec api /bin/bash
    ```

* To restart qcluster automatically after code changes, follow the steps below:

    ```
    pip install -r requirements.dev.txt
    python q_cluster_watcher.py
    ```
### Running Tests

* Add this to you Dockerfile before the # set environment variables step:
    ```
    # install the requirements from the requirements.txt file via git
    RUN apt-get update && apt-get install git -y --no-install-recommends

    ARG CI
    RUN if [ "$CI" = "ENABLED" ]; then \
            apt-get install lsb-release gnupg2 wget -y --no-install-recommends; \
            apt-cache search postgresql | grep postgresql; \
            sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list'; \
            wget --no-check-certificate --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add - ; \
            apt -y update; \
            apt-get install postgresql-14 -y --no-install-recommends; \
        fi
    ```
* Add the following environment variables to setup.sh file

    ```
    export FYLE_BASE_URL=<fyle base url>
    export FYLE_CLIENT_ID=<client_id>
    export FYLE_CLIENT_SECRET=<client_secret>
    export FYLE_REFRESH_TOKEN=<refresh_token>
    export FYLE_TOKEN_URI=<fyle token uri>
    export QBO_CLIENT_ID=<qbo client id>
    export QBO_CLIENT_SECRET=<qbo client secret>
    export QBO_REDIRECT_URI=<qbo redirect uri>
    export QBO_TOKEN_URI=<qbo token uri>
    export QBO_ENVIRONMENT=<qbo environment>
    ```

* Run the following commands

    1. source setup.sh
    2. docker-compose -f docker-compose-pipeline.yml build
    3. docker-compose -f docker-compose-pipeline.yml up -d
    4. docker-compose -f docker-compose-pipeline.yml exec api pytest tests/

    If the test_check_toekn_health() test fails then generate new refresh tokens and place them in
    test_refresh_token.txt file

* Run the following command to update tests SQL fixture (`tests/sql_fixtures/reset_db_fixtures/reset_db.sql`)
    ```
    docker-compose -f docker-compose-pipeline.yml exec api /bin/bash tests/sql_fixtures/migration_fixtures/create_migration.sh
    ```

### Working with pre commit hooks ###
* Run below command to install pre commit, if it is not already installed.
pre commit version must be at least 3.3.1.
```shell
brew install pre-commit
```
* To set up pre commit hook in your local development environment run below command.
This step may take a little longer to complete.
Once done pre commit hooks will automatically run on changed files when you do `git commit`.
```shell
pre-commit install --install-hooks
```
* To run pre commit hooks on all files run below command
```shell
pre-commit run --all-files
```

* To skip pre commit hooks in case of emergency
```shell
git commit --no-verify -m "Commit_message"
```
