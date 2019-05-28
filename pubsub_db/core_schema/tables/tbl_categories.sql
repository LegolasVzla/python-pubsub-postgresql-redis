--DROP TABLE IF EXISTS core_schema.tbl_categories;
CREATE TABLE core_schema.tbl_categories (
	categories_id SERIAL NOT NULL PRIMARY KEY,
	name VARCHAR(255),
	order_by INTEGER,
	is_active BOOLEAN DEFAULT true,
	is_deleted BOOLEAN DEFAULT false,
    last_modified_date timestamp with time zone
);
