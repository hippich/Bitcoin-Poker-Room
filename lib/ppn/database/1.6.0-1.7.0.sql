UPDATE server SET version = '1.7.0';
--
-- Larger field for skin url 
--
ALTER TABLE `users` CHANGE COLUMN `skin_url` `skin_url` VARCHAR(255);
--
-- Server side, per user locale
-- 
ALTER TABLE `users` ADD COLUMN `locale` VARCHAR(32) DEFAULT "en_US";
--
-- There may be multiple users
ALTER TABLE `users` DROP INDEX `name_idx`, ADD INDEX `name_idx` ( `name` );
--
-- Larger field for tourney name
--
ALTER TABLE `tourneys` CHANGE COLUMN `name` `name` VARCHAR(200);
ALTER TABLE `tourneys_schedule` CHANGE COLUMN `name` `name` VARCHAR(200);
--
-- Tournament state is used for tourneySelect
--
ALTER TABLE `tourneys` ADD KEY ( `state` ) ;
--
-- Tournaments may be owned by a server.
--
ALTER TABLE `tourneys` ADD COLUMN resthost_serial INT UNSIGNED DEFAULT 0 NOT NULL;
ALTER TABLE `tourneys_schedule` ADD COLUMN resthost_serial INT UNSIGNED DEFAULT 0 NOT NULL;
ALTER TABLE `tourneys_schedule` ADD COLUMN currency_serial_from_date_format VARCHAR(16) DEFAULT NULL;
--
-- Tournament rank is used for tourneySelect
--
ALTER TABLE `user2tourney` ADD KEY ( `rank` ) ;
--
-- Currency serial is redundant but commonly used in requests
-- and duplication saves joins.
--
ALTER TABLE `user2tourney` ADD COLUMN currency_serial INT UNSIGNED NOT NULL;
ALTER TABLE `user2tourney` ADD KEY ( `user_serial`, `currency_serial`, `rank` ) ;
--
-- History of monitor events
--
CREATE TABLE monitor (
  serial BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  event TINYINT NOT NULL,
  param1 BIGINT NOT NULL,
  param2 BIGINT NOT NULL,
  param3 BIGINT NOT NULL,

  PRIMARY KEY (serial)
) ENGINE=MyISAM;
--
-- Throw away the tables instead of upgrading the table because 
-- most of it is new anyway and there is no persistent information there.
--
DROP TABLE IF EXISTS pokertables;

CREATE TABLE pokertables (
  serial INT UNSIGNED NOT NULL AUTO_INCREMENT,
  resthost_serial INT UNSIGNED DEFAULT 0 NOT NULL,
  seats TINYINT DEFAULT 10,
  average_pot INT UNSIGNED DEFAULT 0,
  hands_per_hour INT UNSIGNED DEFAULT 0,
  percent_flop TINYINT DEFAULT 0,
  players TINYINT DEFAULT 0,
  observers INT UNSIGNED DEFAULT 0,
  waiting TINYINT DEFAULT 0,
  player_timeout INT UNSIGNED DEFAULT 60,
  muck_timeout INT UNSIGNED DEFAULT 5,
  currency_serial INT NOT NULL,
  name VARCHAR(255) NOT NULL UNIQUE,
  variant VARCHAR(255) NOT NULL,
  betting_structure VARCHAR(255) NOT NULL,
  skin VARCHAR(255) DEFAULT "default" NOT NULL,
  tourney_serial INT UNSIGNED DEFAULT 0 NOT NULL,

  PRIMARY KEY (serial),
  KEY (name),
  KEY (variant),
  KEY (resthost_serial)
)  ENGINE=InnoDB CHARSET=utf8;

DROP TABLE IF EXISTS resthost;

CREATE TABLE resthost (
  serial INT UNSIGNED NOT NULL AUTO_INCREMENT,
  name VARCHAR(255),
  host VARCHAR(255),
  port INT UNSIGNED,
  path VARCHAR(255),

  PRIMARY KEY (serial)
) ENGINE=MEMORY;

DROP TABLE IF EXISTS route;

CREATE TABLE route (
  table_serial INT UNSIGNED,
  tourney_serial INT UNSIGNED,
  modified INT UNSIGNED,
  resthost_serial INT UNSIGNED,
  
  PRIMARY KEY (table_serial, tourney_serial),
  KEY (table_serial),
  KEY (tourney_serial),
  KEY (modified),
  KEY (resthost_serial)
) ENGINE=MEMORY;
