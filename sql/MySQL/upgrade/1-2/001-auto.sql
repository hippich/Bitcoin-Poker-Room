-- Convert schema '/home/pavel/projects/poker/Room/script/../sql/_source/deploy/1/001-auto.yml' to '/home/pavel/projects/poker/Room/script/../sql/_source/deploy/2/001-auto.yml':;

;
BEGIN;

;
ALTER TABLE currencies ADD COLUMN rate decimal(64, 4) NOT NULL DEFAULT 0.0000,
                       ADD COLUMN id char(255) NOT NULL;

;

COMMIT;

