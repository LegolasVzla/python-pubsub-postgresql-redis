psql -U postgres -a -f ./main_database.sql
psql -U postgres -d pubsub_db -a -c "CREATE SCHEMA core_schema;"
psql -U postgres -d pubsub_db -a -f ./core_schema/tables/tbl_brands.sql
psql -U postgres -d pubsub_db -a -f ./core_schema/tables/tbl_categories.sql
psql -U postgres -d pubsub_db -a -f ./core_schema/tables/tbl_brands_categories.sql
psql -U postgres -d pubsub_db -a -f ./core_schema/functions/udf_brands_insert.sql
psql -U postgres -d pubsub_db -a -f ./core_schema/functions/udf_categories_insert.sql
psql -U postgres -d pubsub_db -a -f ./core_schema/functions/udf_brands_categories_insert.sql
psql -U postgres -d pubsub_db -a -f ./core_schema/functions/udf_load_redis_brand.sql
psql -U postgres -d pubsub_db -a -f ./core_schema/functions/udf_load_redis_categories.sql
psql -U postgres -d pubsub_db -a -f ./core_schema/functions/udf_load_redis_brands_categories.sql