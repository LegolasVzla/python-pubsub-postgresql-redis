CREATE OR REPLACE FUNCTION core_schema.udf_categories_insert(
    param_name varchar(255)
)
 RETURNS VOID
 LANGUAGE plpgsql
AS $function$
    DECLARE
        local_category_id INTEGER;
        local_notify_payload_resulting VARCHAR;

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

        -- Send notification to python to store in redis (json_build_object 
        -- used with Postgres greater or equal to 9.4)
        local_notify_payload_resulting = (
            SELECT
                json_build_object(
                    'category_id',local_category_id,
                    'name',param_name,
                    'redisHash','tbl_categories_' || param_name
                    )::TEXT
                );
        PERFORM pg_notify (
            'notify_channel_tbl_categories', local_notify_payload_resulting
            );

    END;
    $function$
;
