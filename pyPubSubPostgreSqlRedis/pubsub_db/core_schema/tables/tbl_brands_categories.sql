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

ALTER TABLE core_schema.tbl_brands_categories ADD CONSTRAINT fk_tbl_brands_categories_tbl_brands
FOREIGN KEY (brands_id) REFERENCES core_schema.tbl_brands (brands_id)
ON DELETE CASCADE;

ALTER TABLE core_schema.tbl_brands_categories ADD CONSTRAINT fk_tbl_brands_categories_tbl_categories
FOREIGN KEY (categories_id) REFERENCES core_schema.tbl_categories (categories_id)
ON DELETE CASCADE;
