CREATE TYPE linktype_enum AS ENUM ('ecli', 'eli');
CREATE TABLE "ecli_links" (
    id_internal INT,
    target_type linktype_enum,
    target_identifier TEXT,
    target_label TEXT
);
ALTER TABLE ecli_links ADD PRIMARY KEY (id_internal, target_identifier);
CREATE INDEX ecli_links_idx ON "ecli_links" (id_internal, target_identifier);
