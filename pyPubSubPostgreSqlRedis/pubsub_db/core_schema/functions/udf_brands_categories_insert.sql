CREATE OR REPLACE FUNCTION core_schema.udf_brands_categories_insert(
    param_brand_id INTEGER, 
    param_category_id INTEGER
)
 RETURNS BIT
 LANGUAGE plpgsql
AS $function$
    DECLARE

        local_is_successful BIT := '0';

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
        );

        --PERFORM pg_notify ('notify_channel_notify_channel_tbl_brands_categories', param_brand_id || '_' || param_category_id) ;

        local_is_successful := '1';

        RETURN local_is_successful;

    END;
    $function$
;
