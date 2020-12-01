-- Activate TRGM extension :
-- CREATE EXTENSION pg_trgm;

DROP INDEX IF EXISTS trgm_tags_idx;
DROP TABLE IF EXISTS tags;

CREATE TABLE "tags" (
    id_internal SERIAL PRIMARY KEY,
    tag TEXT,
    meta JSONB,
    date_created TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
-- Use a pirate-worthy index type !
CREATE INDEX trgm_tags_idx ON tags USING GIN (tag gin_trgm_ops);
INSERT INTO tags (tag) VALUES ('COVID-19'), ('anatocisme');
