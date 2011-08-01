UPDATE server SET version = '1.7.5';
--
-- different currencies for buyin and prizes
--
ALTER TABLE `tourneys_schedule` ADD `prize_currency` INT UNSIGNED DEFAULT 0;
ALTER TABLE `tourneys_schedule` ADD `prize_currency_from_date_format` VARCHAR(16) DEFAULT NULL;
ALTER TABLE `tourneys` ADD `prize_currency` INT UNSIGNED DEFAULT 0;
--
-- satellite tournaments
--
ALTER TABLE `tourneys_schedule` ADD `via_satellite` TINYINT DEFAULT 0;
ALTER TABLE `tourneys_schedule` ADD `satellite_of` INT UNSIGNED DEFAULT 0;
ALTER TABLE `tourneys_schedule` ADD `satellite_player_count` INT UNSIGNED DEFAULT 0;
ALTER TABLE `tourneys` ADD `via_satellite` TINYINT DEFAULT 0;
ALTER TABLE `tourneys` ADD `satellite_of` INT UNSIGNED DEFAULT 0;
ALTER TABLE `tourneys` ADD `satellite_player_count` INT UNSIGNED DEFAULT 0;
--
-- pokertables need more indexes for table selection
--
ALTER TABLE `pokertables` ADD INDEX pokertables_players ( `players` ) ; 
ALTER TABLE `pokertables` ADD INDEX pokertables_betting_structure ( `betting_structure` ) ; 
ALTER TABLE `pokertables` ADD INDEX pokertables_currency_serial ( `currency_serial` ) ; 
--
-- Archive chat messages
--
CREATE TABLE chat_messages (
  serial INT UNSIGNED NOT NULL AUTO_INCREMENT,
  player_serial INT UNSIGNED NOT NULL,
  game_id INT UNSIGNED NOT NULL,
  message TEXT DEFAULT '',
  timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  

  PRIMARY KEY (serial)
) ENGINE=MyISAM CHARSET=utf8;
