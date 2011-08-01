-- 
-- Updating the version number makes this script standalone.  It can
-- be applied by an upgrade logic external to poker-network such as
-- dbconfig-common which implements the upgrade logic of
-- pokerdatabase.py. When such a logic is not implemented by a system
-- administration tool (in fedora for instance), pokerdatabaseupgrade
-- can be used by the installation scripts to apply the patches.
--
UPDATE server SET version = '1.0.31';
-- 
-- Money is now a 64 bit value
--
ALTER TABLE `user2money` CHANGE COLUMN `amount` `amount` BIGINT NOT NULL;
ALTER TABLE `user2money` CHANGE COLUMN `rake` `rake` BIGINT DEFAULT 0 NOT NULL;
ALTER TABLE `user2money` CHANGE COLUMN `points` `points` BIGINT DEFAULT 0 NOT NULL;
ALTER TABLE `safe` CHANGE COLUMN `value` `value` BIGINT NOT NULL;
ALTER TABLE `counter` CHANGE COLUMN `value` `value` BIGINT NOT NULL;
--
-- Image is stored in text form
--
ALTER TABLE `users` CHANGE COLUMN `skin_image` `skin_image` TEXT NOT NULL;
ALTER TABLE `users` CHANGE COLUMN `skin_image_type` `skin_image_type` VARCHAR(32) DEFAULT "image/png";
