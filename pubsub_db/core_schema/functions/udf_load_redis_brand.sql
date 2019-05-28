CREATE OR REPLACE FUNCTION core_schema.udf_load_redis_brand()
 RETURNS INTEGER
 LANGUAGE plpgsql
AS $function$
DECLARE

    local_temp_brands RECORD;
    local_notify_payload_resulting VARCHAR;
    local_nrows INTEGER;

BEGIN

	FOR local_temp_brands IN 
      SELECT
        b.brands_id
        ,b.name
      FROM 
        core_schema.tbl_brands b
    LOOP

        SELECT 
            COUNT(b.brands_id) INTO STRICT local_nrows
        FROM
            core_schema.tbl_brands b;

        -- Send notification to python to store in redis (json_build_object 
        -- used with Postgres greater or equal to 9.4)
        local_notify_payload_resulting = (
            SELECT 
                json_build_object(
                    'brand_id',local_temp_brands.brands_id,
                    'name',local_temp_brands.name,
                    'redisHash','tbl_brands_' || local_temp_brands.name
                    )::TEXT
                );
        PERFORM pg_notify (
            'notify_channel_tbl_brands', local_notify_payload_resulting
            );

    END LOOP;

    RETURN local_nrows;

END;

$function$;
