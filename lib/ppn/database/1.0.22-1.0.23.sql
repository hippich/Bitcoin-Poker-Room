-- Avoid stupid errors by making serial unique
ALTER TABLE `currencies` ADD UNIQUE `serial01` ( `serial` );
-- Counter can hold application_data (may be the application transaction id)
ALTER TABLE `counter` ADD `application_data` VARCHAR( 255 ) NOT NULL DEFAULT '';
