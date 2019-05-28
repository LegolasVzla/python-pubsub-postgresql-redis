--DROP TABLE IF EXISTS core_schema.tbl_brands_categories;
CREATE TABLE core_schema.tbl_brands_categories (
	brands_categories_id SERIAL NOT NULL,
	brands_id INTEGER NOT NULL,
	categories_id INTEGER NOT NULL,
	is_active BOOLEAN DEFAULT true,
	is_deleted BOOLEAN DEFAULT false,
    last_modified_date timestamp with time zone,
    PRIMARY KEY (brands_categories_id,brands_id,categories_id)
);
