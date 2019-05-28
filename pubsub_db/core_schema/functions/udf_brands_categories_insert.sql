CREATE OR REPLACE FUNCTION core_schema.udf_brands_categories_insert(
    param_brand_id INTEGER, 
    param_category_id INTEGER
)
 RETURNS VOID
 LANGUAGE plpgsql
AS $function$
    DECLARE
        local_brands_categories_id INTEGER;
        local_notify_payload_resulting VARCHAR;

    BEGIN
        INSERT INTO core_schema.tbl_brands_categories
        (
            brands_id
            , categories_id
            , last_modified_date
        )
        VALUES
        (
            param_brand_id
            , param_category_id
            , CLOCK_TIMESTAMP()
        ) RETURNING brands_categories_id INTO local_brands_categories_id;

        -- Send notification to python to store in redis (json_build_object 
        -- used with Postgres greater or equal to 9.4)
        local_notify_payload_resulting = (
            SELECT 
                json_build_object(
                    'brands_categories_id',local_brands_categories_id,
                    'brand_id',param_brand_id,
                    'categories_id',param_category_id,
                    'redisHash','tbl_brands_categories_' || param_brand_id || '_' || param_category_id
                    )::TEXT
                );
        PERFORM pg_notify (
            'notify_channel_tbl_brands_categories', local_notify_payload_resulting
            );

    END;
    $function$
;
