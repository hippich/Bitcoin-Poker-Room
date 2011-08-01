UPDATE server SET version = '1.7.4';
--
-- user2tourney performances
--
ALTER TABLE user2tourney ADD INDEX tourney_serial (tourney_serial);
--
-- smaller field
--
ALTER TABLE `tourneys` CHANGE COLUMN `state` `state` VARCHAR(16) DEFAULT 'registering';
ALTER TABLE `tourneys` DROP INDEX `state`, ADD INDEX `state` ( `state`, `finish_time` );
