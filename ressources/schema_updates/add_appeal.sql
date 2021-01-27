CREATE TYPE appeal_enum AS ENUM ('yes', 'no', 'nodata');
ALTER TABLE ecli_document ADD COLUMN appeal appeal_enum DEFAULT 'nodata';
