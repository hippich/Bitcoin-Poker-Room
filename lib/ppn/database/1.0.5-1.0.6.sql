--
-- Default play money about is now 1M
--
ALTER TABLE `users` CHANGE `play_money` `play_money` INT( 11 ) NULL DEFAULT '1000000';

--
-- Table holding global server information
--
CREATE TABLE `server` (
`version` VARCHAR( 16 ) NOT NULL
) TYPE = MYISAM ;

insert into server (version) values ('0.0.0');
