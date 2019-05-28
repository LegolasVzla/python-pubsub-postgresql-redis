#!/bin/bash
sudo -u postgres psql -c "DROP DATABASE IF EXISTS pubsub_db;"
sudo -u postgres psql -c "DROP USER IF EXISTS usuario1;"
sudo -u postgres psql -c "CREATE USER usuario1 WITH PASSWORD 'postgresql';"
sudo -u postgres psql -c "ALTER ROLE usuario1 WITH SUPERUSER;"
sudo -u postgres psql -c "CREATE DATABASE pubsub_db WITH OWNER usuario1;"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE pubsub_db TO usuario1;"
sudo -u postgres psql -d pubsub_db -a -c "CREATE SCHEMA core_schema;"
