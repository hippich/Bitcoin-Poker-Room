-- 
-- Created by SQL::Translator::Producer::MySQL
-- Created on Wed Oct 26 07:05:11 2011
-- 
;
SET foreign_key_checks=0;
--
-- Table: `affiliates`
--
CREATE TABLE `affiliates` (
  `serial` integer unsigned NOT NULL auto_increment,
  `modified` timestamp NOT NULL DEFAULT current_timestamp,
  `created` integer unsigned NOT NULL,
  `users_count` integer unsigned DEFAULT 0,
  `users_rake` integer unsigned DEFAULT 0,
  `users_points` integer unsigned DEFAULT 0,
  `share` integer unsigned DEFAULT 0,
  `companyname` varchar(255) DEFAULT '',
  `firstname` varchar(255) DEFAULT '',
  `lastname` varchar(255) DEFAULT '',
  `addr_street` varchar(255) DEFAULT '',
  `addr_street2` varchar(255) DEFAULT '',
  `addr_zip` varchar(64) DEFAULT '',
  `addr_town` varchar(64) DEFAULT '',
  `addr_state` varchar(128) DEFAULT '',
  `addr_country` varchar(64) DEFAULT '',
  `phone` varchar(64) DEFAULT '',
  `url` text,
  `notes` text,
  PRIMARY KEY (`serial`)
);
--
-- Table: `api_users`
--
CREATE TABLE `api_users` (
  `id` integer NOT NULL auto_increment,
  `email` varchar(255) NOT NULL,
  `api_key` varchar(255) NOT NULL,
  `secret` varchar(255) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE `key_secret` (`api_key`, `secret`)
);
--
-- Table: `chat_messages`
--
CREATE TABLE `chat_messages` (
  `serial` integer unsigned NOT NULL auto_increment,
  `player_serial` integer unsigned NOT NULL,
  `game_id` integer unsigned NOT NULL,
  `message` text,
  `timestamp` timestamp NOT NULL DEFAULT current_timestamp,
  PRIMARY KEY (`serial`)
);
--
-- Table: `counter`
--
CREATE TABLE `counter` (
  `transaction_id` char(40) NOT NULL,
  `user_serial` integer NOT NULL,
  `currency_serial` integer NOT NULL,
  `serial` integer NOT NULL,
  `name` char(40) NOT NULL,
  `value` bigint NOT NULL,
  `status` char(1) NOT NULL DEFAULT 'y',
  `application_data` varchar(255) NOT NULL DEFAULT '',
  PRIMARY KEY (`currency_serial`, `serial`, `name`)
);
--
-- Table: `currencies`
--
CREATE TABLE `currencies` (
  `serial` integer NOT NULL auto_increment,
  `url` char(255) NOT NULL,
  `symbol` char(8),
  `name` char(32),
  `cash_out` integer,
  `id` char(255) NOT NULL,
  `rate` decimal(64, 4) NOT NULL DEFAULT 0.0000,
  `minconf` integer NOT NULL DEFAULT 6,
  `class` char(255) NOT NULL,
  PRIMARY KEY (`serial`, `url`),
  UNIQUE `serial` (`serial`),
  UNIQUE `url` (`url`)
) ENGINE=InnoDB;
--
-- Table: `deposits`
--
CREATE TABLE `deposits` (
  `deposit_id` integer NOT NULL auto_increment,
  `user_serial` integer NOT NULL,
  `currency_serial` integer NOT NULL,
  `amount` float NOT NULL,
  `processed` integer NOT NULL,
  `info` text NOT NULL,
  `created_at` datetime NOT NULL,
  `processed_at` datetime NOT NULL,
  PRIMARY KEY (`deposit_id`)
);
--
-- Table: `hands`
--
CREATE TABLE `hands` (
  `serial` integer unsigned NOT NULL auto_increment,
  `created` timestamp NOT NULL DEFAULT current_timestamp,
  `name` varchar(32),
  `description` text NOT NULL,
  PRIMARY KEY (`serial`)
) ENGINE=InnoDB;
--
-- Table: `messages`
--
CREATE TABLE `messages` (
  `serial` integer unsigned NOT NULL auto_increment,
  `send_date` timestamp NOT NULL DEFAULT current_timestamp,
  `message` text,
  `sent` char(1) NOT NULL DEFAULT 'n',
  PRIMARY KEY (`serial`, `send_date`, `sent`)
);
--
-- Table: `monitor`
--
CREATE TABLE `monitor` (
  `serial` bigint unsigned NOT NULL auto_increment,
  `created` timestamp NOT NULL DEFAULT current_timestamp,
  `event` tinyint NOT NULL,
  `param1` bigint NOT NULL,
  `param2` bigint NOT NULL,
  `param3` bigint NOT NULL,
  PRIMARY KEY (`serial`)
);
--
-- Table: `prizes`
--
CREATE TABLE `prizes` (
  `serial` integer NOT NULL auto_increment,
  `name` varchar(255),
  `description` varchar(255),
  `image_url` text,
  `points` integer NOT NULL DEFAULT 0,
  `link_url` text,
  PRIMARY KEY (`serial`)
);
--
-- Table: `prizes_version`
--
CREATE TABLE `prizes_version` (
  `version` varchar(16) NOT NULL
);
--
-- Table: `rank`
--
CREATE TABLE `rank` (
  `user_serial` integer unsigned NOT NULL,
  `currency_serial` integer unsigned NOT NULL,
  `amount` bigint NOT NULL,
  `rank` integer unsigned NOT NULL,
  `percentile` tinyint unsigned NOT NULL DEFAULT 0,
  PRIMARY KEY (`user_serial`, `currency_serial`)
);
--
-- Table: `rank_tmp`
--
CREATE TABLE `rank_tmp` (
  `user_serial` integer unsigned NOT NULL,
  `currency_serial` integer unsigned NOT NULL,
  `amount` bigint NOT NULL,
  `rank` integer unsigned NOT NULL,
  `percentile` tinyint unsigned NOT NULL DEFAULT 0,
  PRIMARY KEY (`user_serial`, `currency_serial`)
);
--
-- Table: `resthost`
--
CREATE TABLE `resthost` (
  `serial` integer unsigned NOT NULL auto_increment,
  `name` varchar(255),
  `host` varchar(255),
  `port` integer unsigned,
  `path` varchar(255),
  PRIMARY KEY (`serial`)
) ENGINE=InnoDB;
--
-- Table: `route`
--
CREATE TABLE `route` (
  `table_serial` integer unsigned NOT NULL DEFAULT 0,
  `tourney_serial` integer unsigned NOT NULL DEFAULT 0,
  `modified` integer unsigned,
  `resthost_serial` integer unsigned,
  PRIMARY KEY (`table_serial`, `tourney_serial`)
);
--
-- Table: `safe`
--
CREATE TABLE `safe` (
  `currency_serial` integer NOT NULL,
  `serial` integer NOT NULL,
  `name` char(40) NOT NULL,
  `value` bigint NOT NULL,
  PRIMARY KEY (`currency_serial`, `serial`, `value`)
);
--
-- Table: `server`
--
CREATE TABLE `server` (
  `version` varchar(16) NOT NULL
);
--
-- Table: `session`
--
CREATE TABLE `session` (
  `user_serial` integer NOT NULL,
  `started` integer DEFAULT 0,
  `ended` integer DEFAULT 0,
  `ip` varchar(16) NOT NULL DEFAULT '',
  PRIMARY KEY (`user_serial`, `ip`)
);
--
-- Table: `session_history`
--
CREATE TABLE `session_history` (
  `user_serial` integer NOT NULL,
  `started` integer DEFAULT 0,
  `ended` integer DEFAULT 0,
  `ip` varchar(16),
  `id` integer NOT NULL auto_increment,
  PRIMARY KEY (`id`)
);
--
-- Table: `tourneys_schedule`
--
CREATE TABLE `tourneys_schedule` (
  `serial` integer unsigned NOT NULL auto_increment,
  `resthost_serial` integer unsigned NOT NULL DEFAULT 0,
  `name` varchar(200),
  `description_short` varchar(64),
  `description_long` text,
  `players_quota` integer DEFAULT 10,
  `players_min` integer DEFAULT 2,
  `variant` varchar(32),
  `betting_structure` varchar(32),
  `seats_per_game` integer DEFAULT 10,
  `player_timeout` integer DEFAULT 60,
  `currency_serial` integer,
  `prize_currency` integer unsigned DEFAULT 0,
  `prize_min` integer DEFAULT 0,
  `bailor_serial` integer DEFAULT 0,
  `buy_in` integer DEFAULT 0,
  `rake` integer DEFAULT 0,
  `sit_n_go` char(1) DEFAULT 'y',
  `breaks_first` integer DEFAULT 7200,
  `breaks_interval` integer DEFAULT 3600,
  `breaks_duration` integer DEFAULT 300,
  `rebuy_delay` integer DEFAULT 0,
  `add_on` integer DEFAULT 0,
  `add_on_delay` integer DEFAULT 60,
  `start_time` integer(11),
  `register_time` integer(11),
  `active` char(1) DEFAULT 'y',
  `respawn` char(1) DEFAULT 'n',
  `respawn_interval` integer DEFAULT 0,
  `currency_serial_from_date_format` varchar(16),
  `prize_currency_from_date_format` varchar(16),
  `satellite_of` integer unsigned DEFAULT 0,
  `via_satellite` tinyint DEFAULT 0,
  `satellite_player_count` integer unsigned DEFAULT 0,
  PRIMARY KEY (`serial`)
);
--
-- Table: `tourneys_schedule2prizes`
--
CREATE TABLE `tourneys_schedule2prizes` (
  `tourneys_schedule_serial` integer,
  `prize_serial` integer
);
--
-- Table: `users`
--
CREATE TABLE `users` (
  `serial` integer unsigned NOT NULL auto_increment,
  `created` integer unsigned NOT NULL,
  `name` varchar(64),
  `email` varchar(128),
  `affiliate` integer unsigned DEFAULT 0,
  `skin_url` varchar(255) DEFAULT 'random',
  `skin_outfit` text,
  `skin_image` text,
  `skin_image_type` varchar(32) DEFAULT 'image/png',
  `password` text NOT NULL,
  `privilege` integer DEFAULT 1,
  `locale` varchar(32) DEFAULT 'en_US',
  `rating` integer DEFAULT 1000,
  `future_rating` float DEFAULT 1000,
  `games_count` integer DEFAULT 0,
  `data` text,
  PRIMARY KEY (`serial`),
  UNIQUE `email_idx` (`email`)
) ENGINE=InnoDB;
--
-- Table: `users_private`
--
CREATE TABLE `users_private` (
  `serial` integer unsigned NOT NULL,
  `firstname` varchar(255) DEFAULT '',
  `lastname` varchar(255) DEFAULT '',
  `addr_street` varchar(255) DEFAULT '',
  `addr_street2` varchar(255) DEFAULT '',
  `addr_zip` varchar(64) DEFAULT '',
  `addr_town` varchar(64) DEFAULT '',
  `addr_state` varchar(128) DEFAULT '',
  `addr_country` varchar(64) DEFAULT '',
  `phone` varchar(64) DEFAULT '',
  `gender` char(1) DEFAULT '',
  `birthdate` date,
  `verified` char(1) DEFAULT 'n',
  `verified_time` integer DEFAULT 0,
  PRIMARY KEY (`serial`)
);
--
-- Table: `users_transactions`
--
CREATE TABLE `users_transactions` (
  `from_serial` integer unsigned NOT NULL,
  `to_serial` integer unsigned NOT NULL,
  `modified` timestamp NOT NULL DEFAULT current_timestamp,
  `amount` integer DEFAULT 0,
  `currency_serial` integer NOT NULL,
  `status` char(1) DEFAULT 'n',
  `notes` text,
  `id` integer NOT NULL auto_increment,
  PRIMARY KEY (`id`)
);
--
-- Table: `tourneys`
--
CREATE TABLE `tourneys` (
  `serial` integer unsigned NOT NULL auto_increment,
  `resthost_serial` integer unsigned NOT NULL DEFAULT 0,
  `name` varchar(200),
  `description_short` varchar(64),
  `description_long` text,
  `players_quota` integer DEFAULT 10,
  `players_min` integer DEFAULT 2,
  `variant` varchar(32),
  `betting_structure` varchar(32),
  `seats_per_game` integer DEFAULT 10,
  `player_timeout` integer DEFAULT 60,
  `currency_serial` integer,
  `prize_currency` integer unsigned DEFAULT 0,
  `prize_min` integer DEFAULT 0,
  `bailor_serial` integer DEFAULT 0,
  `buy_in` integer DEFAULT 0,
  `rake` integer DEFAULT 0,
  `sit_n_go` char(1) DEFAULT 'y',
  `breaks_first` integer DEFAULT 7200,
  `breaks_interval` integer DEFAULT 3600,
  `breaks_duration` integer DEFAULT 300,
  `rebuy_delay` integer DEFAULT 0,
  `add_on` integer DEFAULT 0,
  `add_on_delay` integer DEFAULT 60,
  `start_time` integer(11),
  `satellite_of` integer unsigned DEFAULT 0,
  `via_satellite` tinyint DEFAULT 0,
  `satellite_player_count` integer unsigned DEFAULT 0,
  `finish_time` integer(11),
  `state` varchar(16) DEFAULT 'registering',
  `schedule_serial` integer,
  `add_on_count` integer DEFAULT 0,
  `rebuy_count` integer DEFAULT 0,
  INDEX `tourneys_idx_resthost_serial` (`resthost_serial`),
  PRIMARY KEY (`serial`),
  CONSTRAINT `tourneys_fk_resthost_serial` FOREIGN KEY (`resthost_serial`) REFERENCES `resthost` (`serial`)
) ENGINE=InnoDB;
--
-- Table: `user2bitcoin`
--
CREATE TABLE `user2bitcoin` (
  `serial` bigint unsigned NOT NULL auto_increment,
  `user_serial` bigint unsigned NOT NULL,
  `currency_serial` bigint unsigned NOT NULL,
  `amount` decimal(52, 8) unsigned NOT NULL DEFAULT 0.00000000,
  `address` varchar(40) NOT NULL DEFAULT '',
  INDEX `user2bitcoin_idx_user_serial` (`user_serial`),
  PRIMARY KEY (`serial`),
  CONSTRAINT `user2bitcoin_fk_user_serial` FOREIGN KEY (`user_serial`) REFERENCES `users` (`serial`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;
--
-- Table: `user2money`
--
CREATE TABLE `user2money` (
  `user_serial` integer unsigned NOT NULL,
  `currency_serial` integer unsigned NOT NULL,
  `amount` bigint NOT NULL,
  `rake` bigint NOT NULL DEFAULT 0,
  `points` decimal(64, 4) NOT NULL DEFAULT 0.0000,
  `points_cashed` decimal(64, 4) NOT NULL DEFAULT 0.0000,
  INDEX `user2money_idx_currency_serial` (`currency_serial`),
  PRIMARY KEY (`user_serial`, `currency_serial`),
  CONSTRAINT `user2money_fk_currency_serial` FOREIGN KEY (`currency_serial`) REFERENCES `currencies` (`serial`)
) ENGINE=InnoDB;
--
-- Table: `pokertables`
--
CREATE TABLE `pokertables` (
  `serial` integer unsigned NOT NULL auto_increment,
  `resthost_serial` integer unsigned NOT NULL DEFAULT 0,
  `seats` tinyint DEFAULT 10,
  `average_pot` integer unsigned DEFAULT 0,
  `hands_per_hour` integer unsigned DEFAULT 0,
  `percent_flop` tinyint DEFAULT 0,
  `players` tinyint DEFAULT 0,
  `observers` integer unsigned DEFAULT 0,
  `waiting` tinyint DEFAULT 0,
  `player_timeout` integer unsigned DEFAULT 60,
  `muck_timeout` integer unsigned DEFAULT 5,
  `currency_serial` integer NOT NULL,
  `name` varchar(255) NOT NULL,
  `variant` varchar(255) NOT NULL,
  `betting_structure` varchar(255) NOT NULL,
  `small_blind` bigint unsigned NOT NULL,
  `big_blind` bigint unsigned NOT NULL,
  `ante_value` bigint unsigned NOT NULL,
  `ante_bring_in` bigint unsigned NOT NULL,
  `limit_type` varchar(20) NOT NULL,
  `betting_description` varchar(255) NOT NULL,
  `skin` varchar(255) NOT NULL DEFAULT 'default',
  `tourney_serial` integer unsigned NOT NULL DEFAULT 0,
  INDEX `pokertables_idx_resthost_serial` (`resthost_serial`),
  INDEX `pokertables_idx_tourney_serial` (`tourney_serial`),
  PRIMARY KEY (`serial`),
  UNIQUE `name` (`name`),
  CONSTRAINT `pokertables_fk_resthost_serial` FOREIGN KEY (`resthost_serial`) REFERENCES `resthost` (`serial`),
  CONSTRAINT `pokertables_fk_tourney_serial` FOREIGN KEY (`tourney_serial`) REFERENCES `tourneys` (`serial`)
) ENGINE=InnoDB;
--
-- Table: `user2hand`
--
CREATE TABLE `user2hand` (
  `user_serial` integer NOT NULL,
  `hand_serial` integer NOT NULL,
  `ip6` bigint unsigned,
  `ip` bigint unsigned,
  `share` bigint NOT NULL,
  `pot` bigint NOT NULL,
  `rake` bigint NOT NULL,
  `points` decimal(64, 4) NOT NULL,
  INDEX `user2hand_idx_hand_serial` (`hand_serial`),
  INDEX `user2hand_idx_user_serial` (`user_serial`),
  PRIMARY KEY (`user_serial`, `hand_serial`),
  CONSTRAINT `user2hand_fk_hand_serial` FOREIGN KEY (`hand_serial`) REFERENCES `hands` (`serial`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `user2hand_fk_user_serial` FOREIGN KEY (`user_serial`) REFERENCES `users` (`serial`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;
--
-- Table: `withdrawal`
--
CREATE TABLE `withdrawal` (
  `withdrawal_id` integer NOT NULL auto_increment,
  `user_serial` integer NOT NULL,
  `currency_serial` integer NOT NULL,
  `amount` float NOT NULL,
  `processed` integer NOT NULL,
  `info` text NOT NULL,
  `created_at` datetime NOT NULL,
  `processed_at` datetime NOT NULL,
  `dest` text,
  INDEX `withdrawal_idx_currency_serial` (`currency_serial`),
  INDEX `withdrawal_idx_user_serial` (`user_serial`),
  PRIMARY KEY (`withdrawal_id`),
  CONSTRAINT `withdrawal_fk_currency_serial` FOREIGN KEY (`currency_serial`) REFERENCES `currencies` (`serial`),
  CONSTRAINT `withdrawal_fk_user_serial` FOREIGN KEY (`user_serial`) REFERENCES `users` (`serial`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;
--
-- Table: `user2table`
--
CREATE TABLE `user2table` (
  `user_serial` integer unsigned NOT NULL,
  `table_serial` integer unsigned NOT NULL,
  `money` integer NOT NULL DEFAULT 0,
  `bet` integer NOT NULL DEFAULT 0,
  INDEX `user2table_idx_table_serial` (`table_serial`),
  INDEX `user2table_idx_user_serial` (`user_serial`),
  PRIMARY KEY (`user_serial`, `table_serial`),
  CONSTRAINT `user2table_fk_table_serial` FOREIGN KEY (`table_serial`) REFERENCES `pokertables` (`serial`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `user2table_fk_user_serial` FOREIGN KEY (`user_serial`) REFERENCES `users` (`serial`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;
--
-- Table: `user2tourney`
--
CREATE TABLE `user2tourney` (
  `user_serial` integer NOT NULL,
  `currency_serial` integer unsigned NOT NULL,
  `tourney_serial` integer NOT NULL,
  `table_serial` integer,
  `rank` integer DEFAULT -1,
  INDEX `user2tourney_idx_tourney_serial` (`tourney_serial`),
  INDEX `user2tourney_idx_table_serial` (`table_serial`),
  INDEX `user2tourney_idx_user_serial` (`user_serial`),
  PRIMARY KEY (`user_serial`, `tourney_serial`),
  CONSTRAINT `user2tourney_fk_tourney_serial` FOREIGN KEY (`tourney_serial`) REFERENCES `tourneys` (`serial`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `user2tourney_fk_table_serial` FOREIGN KEY (`table_serial`) REFERENCES `pokertables` (`serial`),
  CONSTRAINT `user2tourney_fk_user_serial` FOREIGN KEY (`user_serial`) REFERENCES `users` (`serial`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;
SET foreign_key_checks=1