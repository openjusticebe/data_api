-- Activate TRGM extension :
-- CREATE EXTENSION pg_trgm;
-- OBSOLETE
DROP INDEX IF EXISTS trgm_tags_idx;
DROP TABLE IF EXISTS tags;
--
DROP INDEX IF EXISTS trgm_labels_idx;
DROP TABLE IF EXISTS labels;
CREATE EXTENSION pg_trgm;

CREATE TABLE "labels" (
    id_internal SERIAL PRIMARY KEY,
    label TEXT,
    category TEXT,
    meta JSONB,
    date_created TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
-- Use a pirate-worthy index type !
CREATE INDEX trgm_labels_idx ON labels USING GIN (label gin_trgm_ops);
INSERT INTO labels (label, category) VALUES ('COVID-19', 'pilot'), ('anatocisme', 'pilot'), ('2020', 'year');
