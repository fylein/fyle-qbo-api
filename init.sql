-- Create the main application database
CREATE DATABASE qbo_db;

-- Drop the test database if it exists
DROP DATABASE IF EXISTS test_qbo_db;

-- Create the test database
CREATE DATABASE test_qbo_db;

-- Connect to test database and load test data
\c test_qbo_db;

-- Load the test data
\i /docker-entrypoint-initdb.d/reset_db.sql
