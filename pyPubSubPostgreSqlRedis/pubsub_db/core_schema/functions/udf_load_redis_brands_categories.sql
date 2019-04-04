CREATE OR REPLACE FUNCTION core_schema.udf_load_redis_brands_categories()
 RETURNS INTEGER
 LANGUAGE plpgsql
AS $function$
DECLARE

    local_temp_brands_categories RECORD;
    local_notify_payload_resulting VARCHAR;
    local_nrows INTEGER;

BEGIN

    FOR local_temp_brands_categories IN 
      SELECT 
        bc.brands_categories_id
        ,bc.brands_id
        ,bc.categories_id
      FROM 
        core_schema.tbl_brands_categories bc
    LOOP

        SELECT 
            COUNT(bc.brands_categories_id) INTO STRICT local_nrows
        FROM
            core_schema.tbl_brands_categories bc;

        -- Send notification to python to store in redis (json_build_object 
        -- used with Postgres greater or equal to 9.4)
        local_notify_payload_resulting = (
            SELECT 
                json_build_object(
                    'brands_categories_id',local_temp_brands_categories.brands_categories_id,
                    'brand_id',local_temp_brands_categories.brands_id,
                    'categories_id',local_temp_brands_categories.categories_id,
                    'redisHash','tbl_brands_categories_' || local_temp_brands_categories.brands_id || '_' || local_temp_brands_categories.categories_id
                    )::TEXT
                );
        PERFORM pg_notify (
            'notify_channel_tbl_brands_categories', local_notify_payload_resulting
            );

    END LOOP;

    RETURN local_nrows;

END;

$function$;
