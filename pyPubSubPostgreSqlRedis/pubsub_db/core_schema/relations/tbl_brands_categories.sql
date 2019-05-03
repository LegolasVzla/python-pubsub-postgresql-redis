ALTER TABLE core_schema.tbl_brands_categories ADD CONSTRAINT fk_tbl_brands_categories_tbl_brands
FOREIGN KEY (brands_id) REFERENCES core_schema.tbl_brands (brands_id)
ON DELETE CASCADE;

ALTER TABLE core_schema.tbl_brands_categories ADD CONSTRAINT fk_tbl_brands_categories_tbl_categories
FOREIGN KEY (categories_id) REFERENCES core_schema.tbl_categories (categories_id)
ON DELETE CASCADE;
