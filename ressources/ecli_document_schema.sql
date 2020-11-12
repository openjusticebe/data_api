CREATE TABLE "ecli_document" (
    id_internal SERIAL PRIMARY KEY,
    country VARCHAR(2),
    court TEXT,
    year INT,
    identifier TEXT,
    text TEXT,
    meta JSONB,
    flags TEXT[],
    date_created TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    date_updated TIMESTAMP WITH TIME ZONE
);

CREATE INDEX ecli_country ON "ecli_document" (country, court, year, identifier);
