CREATE OR REPLACE FUNCTION core_schema.udf_categories_insert(
    param_name varchar(255)
)
 RETURNS INTEGER
 LANGUAGE plpgsql
AS $function$
    DECLARE
        local_category_id INTEGER;

    BEGIN
        INSERT INTO core_schema.tbl_categories
        (
            name
            , last_modified_date
        )
        VALUES
        (
            param_name
            , CLOCK_TIMESTAMP()
        ) RETURNING categories_id INTO local_category_id;

        --PERFORM pg_notify ('notify_channel_tbl_categories', local_category_id || '_' || param_name) ;

        RETURN local_category_id;
    END;
    $function$
;
