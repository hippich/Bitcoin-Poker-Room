UPDATE server SET version = '1.0.33';
--
-- Personal info
--
ALTER TABLE `users_private` ADD COLUMN gender CHAR DEFAULT '';
ALTER TABLE `users_private` ADD COLUMN birthdate DATE;
--
-- Guaranteed prize pool
--
ALTER TABLE `tourneys_schedule` ADD COLUMN prize_min INT DEFAULT 0;
ALTER TABLE `tourneys_schedule` ADD COLUMN bailor_serial INT DEFAULT 0;
ALTER TABLE `tourneys` ADD COLUMN prize_min INT DEFAULT 0;
ALTER TABLE `tourneys` ADD COLUMN bailor_serial INT DEFAULT 0;
--
-- Regular tournaments are canceled if not with a minimum number of players
--
ALTER TABLE `tourneys_schedule` ADD COLUMN players_min INT DEFAULT 0;
ALTER TABLE `tourneys` ADD COLUMN players_min INT DEFAULT 0;
--
-- Control over the table timeout
--
ALTER TABLE `tourneys_schedule` ADD COLUMN player_timeout INT DEFAULT 60;
ALTER TABLE `tourneys` ADD COLUMN player_timeout INT DEFAULT 60;
--
-- Is the schedule entry to be taken in account
--
ALTER TABLE `tourneys_schedule` ADD COLUMN active CHAR DEFAULT 'y';
--
-- Speed up queries by register time
--
ALTER TABLE `tourneys_schedule` ADD INDEX `tourneys_schedule_register_time_index` ( `register_time` );
ALTER TABLE `tourneys_schedule` ADD INDEX `tourneys_schedule_active_index` (`active`);
--
-- Buy in and rake have a default value of zero
--
ALTER TABLE `tourneys` CHANGE COLUMN rake rake INT DEFAULT 0;
ALTER TABLE `tourneys` CHANGE COLUMN buy_in buy_in INT DEFAULT 0;
ALTER TABLE `tourneys_schedule` CHANGE COLUMN rake rake INT DEFAULT 0;
ALTER TABLE `tourneys_schedule` CHANGE COLUMN buy_in buy_in INT DEFAULT 0;
