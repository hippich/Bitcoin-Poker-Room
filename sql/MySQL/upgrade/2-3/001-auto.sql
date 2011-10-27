-- Convert schema '/home/pavel/projects/poker/Room/script/../sql/_source/deploy/2/001-auto.yml' to '/home/pavel/projects/poker/Room/script/../sql/_source/deploy/3/001-auto.yml':;

;
BEGIN;

;
ALTER TABLE currencies ADD COLUMN minconf integer NOT NULL DEFAULT 6,
                       ADD COLUMN class char(255) NOT NULL;

;

COMMIT;

