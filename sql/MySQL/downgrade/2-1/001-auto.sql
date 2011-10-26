-- Convert schema '/home/pavel/projects/poker/Room/script/../sql/_source/deploy/2/001-auto.yml' to '/home/pavel/projects/poker/Room/script/../sql/_source/deploy/1/001-auto.yml':;

;
BEGIN;

;
ALTER TABLE currencies DROP COLUMN rate,
                       DROP COLUMN id;

;

COMMIT;

