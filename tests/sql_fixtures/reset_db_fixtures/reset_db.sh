#!/bin/bash

echo "-------------Populating Test Datebase---------------"
PGPASSWORD=postgres psql -h $DB_HOST -U postgres -c "drop database test_qbo_db";
PGPASSWORD=postgres psql -h $DB_HOST -U postgres -c "create database test_qbo_db";
PGPASSWORD=postgres psql -h $DB_HOST -U postgres test_qbo_db -c "\i tests/sql_fixtures/reset_db_fixtures/reset_db.sql";
echo "---------------------Testing-------------------------"
