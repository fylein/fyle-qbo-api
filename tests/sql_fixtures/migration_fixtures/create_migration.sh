#!/bin/bash

# Setting value for DB Host
export DB_HOST=db


# # Changing the database name to the fixture database
export DATABASE_URL=postgres://postgres:postgres@db:5432/test_qbo_db

# # Running migrations on the fixture database
python manage.py migrate

read -p "Add SQL script paths separated by spaces if any, else press enter to continue? " scripts

read -a paths <<< $scripts

for path in "${paths[@]}"
do
    echo "Running script $path"
    PGPASSWORD=postgres psql -h $DB_HOST -U postgres test_qbo_db -c "\i $path"
done

# creating a dump of the new fixture
PGPASSWORD=postgres pg_dump -U postgres -h db -d test_qbo_db > tests/sql_fixtures/reset_db_fixtures/reset_db.sql
