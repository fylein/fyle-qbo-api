# Fyle QBO API
Django Rest Framework API for Fyle Quickbooks Online Integration


### Setup

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

    1. docker-compose -f docker-compose-pipeline.yml build
    2. docker-compose -f docker-compose-pipeline.yml up -d
    3. docker-compose -f docker-compose-pipeline.yml exec api pytest tests/

* Run the following command to update tests SQL fixture (`tests/sql_fixtures/reset_db_fixtures/reset_db.sql`)
    ```
    docker-compose -f docker-compose-pipeline.yml exec api /bin/bash tests/sql_fixtures/migration_fixtures/create_migration.sh 
    ```
