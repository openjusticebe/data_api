-- Obsolete
DROP INDEX IF EXISTS ecli_country;
--

DROP TYPE IF EXISTS status_enum;
DROP INDEX IF EXISTS ecli_parts;
DROP INDEX IF EXISTS ecli_parts;
DROP TABLE IF EXISTS ecli_document;

CREATE TYPE status_enum AS ENUM ('new', 'public', 'hidden', 'flagged', 'deleted', 'boosted');
CREATE TABLE "ecli_document" (
    id_internal SERIAL PRIMARY KEY,
    hash TEXT,
    ecli TEXT,
    country VARCHAR(2),
    court TEXT,
    year INT,
    identifier TEXT,
    text TEXT,
    meta JSONB,
    flags TEXT[],
    ukey TEXT,
    lang VARCHAR(2),
    status status_enum DEFAULT 'new',
    date_created TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    date_updated TIMESTAMP WITH TIME ZONE
);

CREATE INDEX ecli_parts ON "ecli_document" (country, court, year, identifier);
CREATE INDEX ecli_ecli ON "ecli_document" (ecli);
CREATE INDEX ecli_status ON "ecli_document" (status);
