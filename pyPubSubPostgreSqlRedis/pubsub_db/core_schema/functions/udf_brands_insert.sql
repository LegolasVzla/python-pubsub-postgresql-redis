CREATE OR REPLACE FUNCTION core_schema.udf_brands_insert(
    param_name varchar(255)
)
 RETURNS INTEGER
 LANGUAGE plpgsql
AS $function$
    DECLARE
        local_brand_id INTEGER;

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

        --PERFORM pg_notify ('notify_channel_tbl_brands', local_brand_id || '_' || param_name);

        RETURN local_brand_id;
    END;
    $function$
;
