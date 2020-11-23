CREATE TYPE status_enum AS ENUM ('new', 'public', 'hidden', 'flagged', 'deleted', 'boosted');
ALTER TABLE ecli_document ADD COLUMN status status_enum DEFAULT 'new';
CREATE INDEX ecli_status ON "ecli_document" (status);
