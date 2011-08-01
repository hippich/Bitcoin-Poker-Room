UPDATE server SET version = '1.0.37';
--
-- Fields related to tournament breaks
--
ALTER TABLE `tourneys` ADD COLUMN breaks_first INT DEFAULT 7200;
ALTER TABLE `tourneys` CHANGE COLUMN breaks_interval breaks_interval INT DEFAULT 3600;
ALTER TABLE `tourneys` ADD COLUMN breaks_duration INT DEFAULT 300;
ALTER TABLE `tourneys_schedule` ADD COLUMN breaks_first INT DEFAULT 7200;
ALTER TABLE `tourneys_schedule` CHANGE COLUMN breaks_interval breaks_interval INT DEFAULT 3600;
ALTER TABLE `tourneys_schedule` ADD COLUMN breaks_duration INT DEFAULT 300;
