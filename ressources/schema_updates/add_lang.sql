ALTER TABLE ecli_document ADD COLUMN ark TEXT;
CREATE INDEX ecli_document_ark ON "ecli_document" (ark);
