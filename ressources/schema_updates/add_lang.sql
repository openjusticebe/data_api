ALTER TABLE ecli_document ADD COLUMN ark TEXT
CREATE UNIQUE INDEX ecli_document_ark ON "ecli_document" (ark);
