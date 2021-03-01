ALTER TABLE ecli_document
    ADD COLUMN views_hash INT DEFAULT 0,
    ADD COLUMN views_public INT DEFAULT 0
;
