CREATE OR REPLACE FUNCTION core_schema.udf_load_redis_categories()
 RETURNS INTEGER
 LANGUAGE plpgsql
AS $function$
DECLARE

    local_temp_categories RECORD;
    local_notify_payload_resulting VARCHAR;
    local_nrows INTEGER;

BEGIN
     
    FOR local_temp_categories IN 
      SELECT 
        c.categories_id
        ,c.name
      FROM 
        core_schema.tbl_categories c
    LOOP

        SELECT 
            COUNT(c.categories_id) INTO STRICT local_nrows
        FROM
            core_schema.tbl_categories c;

        -- Send notification to python to store in redis (json_build_object 
        -- used with Postgres greater or equal to 9.4)
        local_notify_payload_resulting = (
            SELECT
                json_build_object(
                    'category_id',local_temp_categories.categories_id,
                    'name',local_temp_categories.name,
                    'redisHash','tbl_categories_' || local_temp_categories.name
                    )::TEXT
                );
        PERFORM pg_notify (
            'notify_channel_tbl_categories', local_notify_payload_resulting
            );

    END LOOP;

    RETURN local_nrows;

END;

$function$;
