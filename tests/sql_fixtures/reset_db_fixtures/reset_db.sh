echo "-------------Populating Test Datebase---------------"
# psql postgres -c "drop database test_qbo";
# psql postgres -c "create database test_qbo";
# psql test_qbo < "tests/sql_fixtures/reset_db_fixtures/reset_db.sql";
echo "---------------------Testing-------------------------"