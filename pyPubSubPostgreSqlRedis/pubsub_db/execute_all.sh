#!/bin/bash
#sudo -u postgres psql -a -f ./main_database.sh
sudo -u postgres psql -c "DROP DATABASE IF EXISTS pubsub_db;"
sudo -u postgres psql -c "DROP USER IF EXISTS postgres_db_user;"
sudo -u postgres psql -c "CREATE USER postgres_db_user WITH PASSWORD 'postgres_db_pass';"
sudo -u postgres psql -c "ALTER ROLE postgres_db_user WITH SUPERUSER;"
sudo -u postgres psql -c "CREATE DATABASE pubsub_db WITH OWNER postgres_db_user;"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE pubsub_db TO postgres_db_user;"
sudo -u postgres psql -d pubsub_db -a -c "CREATE SCHEMA core_schema;"
sudo -u postgres psql -d pubsub_db -a -f ./core_schema/tables/tbl_brands.sql
sudo -u postgres psql -d pubsub_db -a -f ./core_schema/tables/tbl_categories.sql
sudo -u postgres psql -d pubsub_db -a -f ./core_schema/tables/tbl_brands_categories.sql
sudo -u postgres psql -d pubsub_db -a -f ./core_schema/functions/udf_brands_insert.sql
sudo -u postgres psql -d pubsub_db -a -f ./core_schema/functions/udf_categories_insert.sql
sudo -u postgres psql -d pubsub_db -a -f ./core_schema/functions/udf_brands_categories_insert.sql
sudo -u postgres psql -d pubsub_db -a -f ./core_schema/functions/udf_load_redis_brand.sql
sudo -u postgres psql -d pubsub_db -a -f ./core_schema/functions/udf_load_redis_categories.sql
sudo -u postgres psql -d pubsub_db -a -f ./core_schema/functions/udf_load_redis_brands_categories.sql
