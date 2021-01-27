-- Obsolete
DROP INDEX IF EXISTS ecli_country;
--

DROP TYPE IF EXISTS status_enum;
DROP TYPE IF EXISTS linktype_enum;
DROP INDEX IF EXISTS ecli_parts;
DROP INDEX IF EXISTS ecli_parts;
DROP TABLE IF EXISTS ecli_document;
DROP TABLE IF EXISTS ecli_links;

CREATE TYPE status_enum AS ENUM ('new', 'public', 'hidden', 'flagged', 'deleted', 'boosted');
CREATE TYPE linktype_enum AS ENUM ('ecli', 'eli');
CREATE TYPE appeal_enum AS ENUM ('yes', 'no', 'nodata');
CREATE TABLE "ecli_document" (
    id_internal SERIAL PRIMARY KEY,
    hash TEXT,
    ecli TEXT,
    country VARCHAR(2),
    court TEXT,
    year INT,
    identifier TEXT,
    text TEXT,
    appeal appeal_enum DEFAULT 'nodata',
    meta JSONB,
    flags TEXT[],
    ukey TEXT,
    lang VARCHAR(2),
    status status_enum DEFAULT 'new',
    date_created TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    date_updated TIMESTAMP WITH TIME ZONE
);

CREATE TABLE "ecli_links" (
    id_internal INT,
    target_type linktype_enum,
    target_identifier TEXT,
    target_label TEXT
);
ALTER TABLE ecli_links ADD PRIMARY KEY (id_internal, target_identifier);
CREATE INDEX ecli_links_idx ON "ecli_links" (id_internal, target_identifier);
CREATE INDEX ecli_parts ON "ecli_document" (country, court, year, identifier);
CREATE INDEX ecli_ecli ON "ecli_document" (ecli);
CREATE INDEX ecli_status ON "ecli_document" (status);
