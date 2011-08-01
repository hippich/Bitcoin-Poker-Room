UPDATE server SET version = '1.5.0';
--
-- Larger field for user names
--
ALTER TABLE `users` CHANGE COLUMN `name` `name` VARCHAR(64);
