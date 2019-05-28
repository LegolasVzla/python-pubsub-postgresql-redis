CREATE OR REPLACE FUNCTION core_schema.udf_brands_insert(
    param_name varchar(255)
)
 RETURNS VOID
 LANGUAGE plpgsql
AS $function$
    DECLARE
        local_brand_id INTEGER;
        local_notify_payload_resulting VARCHAR;

    BEGIN
        INSERT INTO core_schema.tbl_brands
        (
            name
            , last_modified_date
        )
        VALUES
        (
            param_name
            , CLOCK_TIMESTAMP()
        ) RETURNING brands_id INTO local_brand_id;

        -- Send notification to python to store in redis (json_build_object 
        -- used with Postgres greater or equal to 9.4)
        local_notify_payload_resulting = (
            SELECT 
                json_build_object(
                    'brand_id',local_brand_id,
                    'name',param_name,
                    'redisHash','tbl_brands_' || param_name
                    )::TEXT
                );
        PERFORM pg_notify (
            'notify_channel_tbl_brands', local_notify_payload_resulting
            );

    END;
    $function$
;
