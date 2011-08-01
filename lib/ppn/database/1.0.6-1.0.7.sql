--
-- Default value for skin_url is random
--
ALTER TABLE `users` CHANGE `skin_url` `skin_url` VARCHAR( 32 ) NULL DEFAULT 'random';
UPDATE users SET skin_url = "random" WHERE skin_url = "default";
