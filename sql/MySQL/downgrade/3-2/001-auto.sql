-- Convert schema '/home/pavel/projects/poker/Room/script/../sql/_source/deploy/3/001-auto.yml' to '/home/pavel/projects/poker/Room/script/../sql/_source/deploy/2/001-auto.yml':;

;
BEGIN;

;
ALTER TABLE currencies DROP COLUMN minconf,
                       DROP COLUMN class;

;

COMMIT;

