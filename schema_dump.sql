-- MySQL dump 10.13  Distrib 5.1.41, for debian-linux-gnu (x86_64)
--
-- Host: localhost    Database: pythonpokernetwork
-- ------------------------------------------------------
-- Server version	5.1.41-3ubuntu12.6

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `affiliates`
--

DROP TABLE IF EXISTS `affiliates`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `affiliates` (
  `serial` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `modified` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `created` int(10) unsigned NOT NULL,
  `users_count` int(10) unsigned DEFAULT '0',
  `users_rake` int(10) unsigned DEFAULT '0',
  `users_points` int(10) unsigned DEFAULT '0',
  `share` int(10) unsigned DEFAULT '0',
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `chat_messages`
--

DROP TABLE IF EXISTS `chat_messages`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `chat_messages` (
  `serial` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `player_serial` int(10) unsigned NOT NULL,
  `game_id` int(10) unsigned NOT NULL,
  `message` text,
  `timestamp` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`serial`)
) ENGINE=MyISAM AUTO_INCREMENT=20 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `counter`
--

DROP TABLE IF EXISTS `counter`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `counter` (
  `transaction_id` char(40) NOT NULL,
  `user_serial` int(11) NOT NULL,
  `currency_serial` int(11) NOT NULL,
  `serial` int(11) NOT NULL,
  `name` char(40) NOT NULL,
  `value` bigint(20) NOT NULL,
  `status` char(1) NOT NULL DEFAULT 'y',
  `application_data` varchar(255) NOT NULL DEFAULT '',
  PRIMARY KEY (`currency_serial`,`name`,`serial`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `currencies`
--

DROP TABLE IF EXISTS `currencies`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `currencies` (
  `serial` int(11) NOT NULL AUTO_INCREMENT,
  `url` char(255) NOT NULL,
  `symbol` char(8) DEFAULT NULL,
  `name` char(32) DEFAULT NULL,
  `cash_out` int(11) DEFAULT NULL,
  PRIMARY KEY (`serial`,`url`),
  UNIQUE KEY `serial` (`serial`),
  UNIQUE KEY `url` (`url`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `deposits`
--

DROP TABLE IF EXISTS `deposits`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `deposits` (
  `deposit_id` int(11) NOT NULL AUTO_INCREMENT,
  `user_serial` int(11) NOT NULL,
  `currency_serial` int(11) NOT NULL,
  `amount` float NOT NULL,
  `processed` int(11) NOT NULL,
  `info` text NOT NULL,
  `created_at` datetime NOT NULL,
  `processed_at` datetime NOT NULL,
  PRIMARY KEY (`deposit_id`),
  KEY `user_serial` (`user_serial`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `hands`
--

DROP TABLE IF EXISTS `hands`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `hands` (
  `serial` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `created` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `name` varchar(32) DEFAULT NULL,
  `description` text NOT NULL,
  PRIMARY KEY (`serial`)
) ENGINE=InnoDB AUTO_INCREMENT=170 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `messages`
--

DROP TABLE IF EXISTS `messages`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `messages` (
  `serial` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `send_date` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `message` text,
  `sent` char(1) NOT NULL DEFAULT 'n',
  PRIMARY KEY (`serial`,`send_date`,`sent`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `monitor`
--

DROP TABLE IF EXISTS `monitor`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `monitor` (
  `serial` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `created` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `event` tinyint(4) NOT NULL,
  `param1` bigint(20) NOT NULL,
  `param2` bigint(20) NOT NULL,
  `param3` bigint(20) NOT NULL,
  PRIMARY KEY (`serial`)
) ENGINE=MyISAM AUTO_INCREMENT=494 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `pokertables`
--

DROP TABLE IF EXISTS `pokertables`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `pokertables` (
  `serial` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `resthost_serial` int(10) unsigned NOT NULL DEFAULT '0',
  `seats` tinyint(4) DEFAULT '10',
  `average_pot` int(10) unsigned DEFAULT '0',
  `hands_per_hour` int(10) unsigned DEFAULT '0',
  `percent_flop` tinyint(4) DEFAULT '0',
  `players` tinyint(4) DEFAULT '0',
  `observers` int(10) unsigned DEFAULT '0',
  `waiting` tinyint(4) DEFAULT '0',
  `player_timeout` int(10) unsigned DEFAULT '60',
  `muck_timeout` int(10) unsigned DEFAULT '5',
  `currency_serial` int(11) NOT NULL,
  `name` varchar(255) NOT NULL,
  `variant` varchar(255) NOT NULL,
  `betting_structure` varchar(255) NOT NULL,
  `skin` varchar(255) NOT NULL DEFAULT 'default',
  `tourney_serial` int(10) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`serial`),
  UNIQUE KEY `name` (`name`),
  KEY `pokertables_name` (`name`),
  KEY `pokertables_variant` (`variant`),
  KEY `pokertables_players` (`players`),
  KEY `pokertables_betting_structure` (`betting_structure`),
  KEY `pokertables_currency_serial` (`currency_serial`),
  KEY `resthost_serial` (`resthost_serial`)
) ENGINE=InnoDB AUTO_INCREMENT=41 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `prizes`
--

DROP TABLE IF EXISTS `prizes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `prizes` (
  `serial` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) DEFAULT NULL,
  `description` varchar(255) DEFAULT NULL,
  `image_url` text,
  `points` int(10) NOT NULL DEFAULT '0',
  `link_url` text,
  PRIMARY KEY (`serial`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `prizes_version`
--

DROP TABLE IF EXISTS `prizes_version`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `prizes_version` (
  `version` varchar(16) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `rank`
--

DROP TABLE IF EXISTS `rank`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `rank` (
  `user_serial` int(10) unsigned NOT NULL,
  `currency_serial` int(10) unsigned NOT NULL,
  `amount` bigint(20) NOT NULL,
  `rank` int(10) unsigned NOT NULL,
  `percentile` tinyint(3) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`user_serial`,`currency_serial`),
  KEY `currency_serial` (`currency_serial`,`amount`),
  KEY `amount` (`amount`),
  KEY `currency_serial_2` (`currency_serial`),
  KEY `rank` (`rank`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `rank_tmp`
--

DROP TABLE IF EXISTS `rank_tmp`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `rank_tmp` (
  `user_serial` int(10) unsigned NOT NULL,
  `currency_serial` int(10) unsigned NOT NULL,
  `amount` bigint(20) NOT NULL,
  `rank` int(10) unsigned NOT NULL,
  `percentile` tinyint(3) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`user_serial`,`currency_serial`),
  KEY `currency_serial` (`currency_serial`,`amount`),
  KEY `amount` (`amount`),
  KEY `currency_serial_2` (`currency_serial`),
  KEY `rank` (`rank`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `resthost`
--

DROP TABLE IF EXISTS `resthost`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `resthost` (
  `serial` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(255) DEFAULT NULL,
  `host` varchar(255) DEFAULT NULL,
  `port` int(10) unsigned DEFAULT NULL,
  `path` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`serial`)
) ENGINE=MEMORY DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `route`
--

DROP TABLE IF EXISTS `route`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `route` (
  `table_serial` int(10) unsigned NOT NULL DEFAULT '0',
  `tourney_serial` int(10) unsigned NOT NULL DEFAULT '0',
  `modified` int(10) unsigned DEFAULT NULL,
  `resthost_serial` int(10) unsigned DEFAULT NULL,
  PRIMARY KEY (`table_serial`,`tourney_serial`),
  KEY `table_serial` (`table_serial`),
  KEY `tourney_serial` (`tourney_serial`),
  KEY `modified` (`modified`),
  KEY `resthost_serial` (`resthost_serial`)
) ENGINE=MEMORY DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `safe`
--

DROP TABLE IF EXISTS `safe`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `safe` (
  `currency_serial` int(11) NOT NULL,
  `serial` int(11) NOT NULL,
  `name` char(40) NOT NULL,
  `value` bigint(20) NOT NULL,
  PRIMARY KEY (`currency_serial`,`serial`,`value`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `server`
--

DROP TABLE IF EXISTS `server`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `server` (
  `version` varchar(16) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `session`
--

DROP TABLE IF EXISTS `session`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `session` (
  `user_serial` int(11) NOT NULL,
  `started` int(11) DEFAULT '0',
  `ended` int(11) DEFAULT '0',
  `ip` varchar(16) NOT NULL DEFAULT '',
  PRIMARY KEY (`user_serial`,`ip`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `session_history`
--

DROP TABLE IF EXISTS `session_history`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `session_history` (
  `user_serial` int(11) NOT NULL,
  `started` int(11) DEFAULT '0',
  `ended` int(11) DEFAULT '0',
  `ip` varchar(16) DEFAULT NULL,
  `id` int(11) NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (`id`),
  KEY `session_history_serial` (`user_serial`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `tourneys`
--

DROP TABLE IF EXISTS `tourneys`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tourneys` (
  `serial` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `resthost_serial` int(10) unsigned NOT NULL DEFAULT '0',
  `name` varchar(200) DEFAULT NULL,
  `description_short` varchar(64) DEFAULT NULL,
  `description_long` text,
  `players_quota` int(11) DEFAULT '10',
  `players_min` int(11) DEFAULT '2',
  `variant` varchar(32) DEFAULT NULL,
  `betting_structure` varchar(32) DEFAULT NULL,
  `seats_per_game` int(11) DEFAULT '10',
  `player_timeout` int(11) DEFAULT '60',
  `currency_serial` int(11) DEFAULT NULL,
  `prize_currency` int(10) unsigned DEFAULT '0',
  `prize_min` int(11) DEFAULT '0',
  `bailor_serial` int(11) DEFAULT '0',
  `buy_in` int(11) DEFAULT '0',
  `rake` int(11) DEFAULT '0',
  `sit_n_go` char(1) DEFAULT 'y',
  `breaks_first` int(11) DEFAULT '7200',
  `breaks_interval` int(11) DEFAULT '3600',
  `breaks_duration` int(11) DEFAULT '300',
  `rebuy_delay` int(11) DEFAULT '0',
  `add_on` int(11) DEFAULT '0',
  `add_on_delay` int(11) DEFAULT '60',
  `start_time` int(11) DEFAULT '0',
  `satellite_of` int(10) unsigned DEFAULT '0',
  `via_satellite` tinyint(4) DEFAULT '0',
  `satellite_player_count` int(10) unsigned DEFAULT '0',
  `finish_time` int(11) DEFAULT '0',
  `state` varchar(16) DEFAULT 'registering',
  `schedule_serial` int(11) DEFAULT NULL,
  `add_on_count` int(11) DEFAULT '0',
  `rebuy_count` int(11) DEFAULT '0',
  PRIMARY KEY (`serial`),
  KEY `tourneys_start_time_index` (`start_time`),
  KEY `state` (`state`,`finish_time`)
) ENGINE=InnoDB AUTO_INCREMENT=508 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `tourneys_schedule`
--

DROP TABLE IF EXISTS `tourneys_schedule`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tourneys_schedule` (
  `serial` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `resthost_serial` int(10) unsigned NOT NULL DEFAULT '0',
  `name` varchar(200) DEFAULT NULL,
  `description_short` varchar(64) DEFAULT NULL,
  `description_long` text,
  `players_quota` int(11) DEFAULT '10',
  `players_min` int(11) DEFAULT '2',
  `variant` varchar(32) DEFAULT NULL,
  `betting_structure` varchar(32) DEFAULT NULL,
  `seats_per_game` int(11) DEFAULT '10',
  `player_timeout` int(11) DEFAULT '60',
  `currency_serial` int(11) DEFAULT NULL,
  `prize_currency` int(10) unsigned DEFAULT '0',
  `prize_min` int(11) DEFAULT '0',
  `bailor_serial` int(11) DEFAULT '0',
  `buy_in` int(11) DEFAULT '0',
  `rake` int(11) DEFAULT '0',
  `sit_n_go` char(1) DEFAULT 'y',
  `breaks_first` int(11) DEFAULT '7200',
  `breaks_interval` int(11) DEFAULT '3600',
  `breaks_duration` int(11) DEFAULT '300',
  `rebuy_delay` int(11) DEFAULT '0',
  `add_on` int(11) DEFAULT '0',
  `add_on_delay` int(11) DEFAULT '60',
  `start_time` int(11) DEFAULT '0',
  `register_time` int(11) DEFAULT '0',
  `active` char(1) DEFAULT 'y',
  `respawn` char(1) DEFAULT 'n',
  `respawn_interval` int(11) DEFAULT '0',
  `currency_serial_from_date_format` varchar(16) DEFAULT NULL,
  `prize_currency_from_date_format` varchar(16) DEFAULT NULL,
  `satellite_of` int(10) unsigned DEFAULT '0',
  `via_satellite` tinyint(4) DEFAULT '0',
  `satellite_player_count` int(10) unsigned DEFAULT '0',
  PRIMARY KEY (`serial`),
  KEY `tourneys_schedule_active_index` (`active`),
  KEY `tourneys_schedule_register_time_index` (`register_time`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `tourneys_schedule2prizes`
--

DROP TABLE IF EXISTS `tourneys_schedule2prizes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tourneys_schedule2prizes` (
  `tourneys_schedule_serial` int(11) DEFAULT NULL,
  `prize_serial` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `user2hand`
--

DROP TABLE IF EXISTS `user2hand`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `user2hand` (
  `user_serial` int(11) NOT NULL,
  `hand_serial` int(11) NOT NULL,
  PRIMARY KEY (`user_serial`,`hand_serial`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `user2money`
--

DROP TABLE IF EXISTS `user2money`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `user2money` (
  `user_serial` int(10) unsigned NOT NULL,
  `currency_serial` int(10) unsigned NOT NULL,
  `amount` bigint(20) NOT NULL,
  `rake` bigint(20) NOT NULL DEFAULT '0',
  `points` bigint(20) NOT NULL DEFAULT '0',
  PRIMARY KEY (`user_serial`,`currency_serial`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `user2table`
--

DROP TABLE IF EXISTS `user2table`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `user2table` (
  `user_serial` int(10) unsigned NOT NULL,
  `table_serial` int(10) unsigned NOT NULL,
  `money` int(11) NOT NULL DEFAULT '0',
  `bet` int(11) NOT NULL DEFAULT '0',
  PRIMARY KEY (`user_serial`,`table_serial`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `user2tourney`
--

DROP TABLE IF EXISTS `user2tourney`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `user2tourney` (
  `user_serial` int(11) NOT NULL,
  `currency_serial` int(10) unsigned NOT NULL,
  `tourney_serial` int(11) NOT NULL,
  `table_serial` int(11) DEFAULT NULL,
  `rank` int(11) DEFAULT '-1',
  PRIMARY KEY (`user_serial`,`tourney_serial`),
  KEY `user_serial` (`user_serial`,`currency_serial`,`tourney_serial`),
  KEY `rank` (`rank`),
  KEY `tourney_serial` (`tourney_serial`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `users` (
  `serial` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `created` int(10) unsigned NOT NULL,
  `name` varchar(64) DEFAULT NULL,
  `email` varchar(128) DEFAULT NULL,
  `affiliate` int(10) unsigned DEFAULT '0',
  `skin_url` varchar(255) DEFAULT 'random',
  `skin_outfit` text,
  `skin_image` text,
  `skin_image_type` varchar(32) DEFAULT 'image/png',
  `password` varchar(512) DEFAULT NULL,
  `privilege` int(11) DEFAULT '1',
  `locale` varchar(32) DEFAULT 'en_US',
  `rating` int(11) DEFAULT '1000',
  `future_rating` float DEFAULT '1000',
  `games_count` int(11) DEFAULT '0',
  `data` text,
  PRIMARY KEY (`serial`),
  UNIQUE KEY `email_idx` (`email`),
  KEY `name_idx` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=22 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `users_private`
--

DROP TABLE IF EXISTS `users_private`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `users_private` (
  `serial` int(10) unsigned NOT NULL,
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
  `birthdate` date DEFAULT NULL,
  `verified` char(1) DEFAULT 'n',
  `verified_time` int(11) DEFAULT '0',
  PRIMARY KEY (`serial`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `users_transactions`
--

DROP TABLE IF EXISTS `users_transactions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `users_transactions` (
  `from_serial` int(10) unsigned NOT NULL,
  `to_serial` int(10) unsigned NOT NULL,
  `modified` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `amount` int(11) DEFAULT '0',
  `currency_serial` int(11) NOT NULL,
  `status` char(1) DEFAULT 'n',
  `notes` text,
  `id` int(11) NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (`id`),
  KEY `from_serial` (`from_serial`,`to_serial`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `withdrawal`
--

DROP TABLE IF EXISTS `withdrawal`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `withdrawal` (
  `withdrawal_id` int(11) NOT NULL AUTO_INCREMENT,
  `user_serial` int(11) NOT NULL,
  `currency_serial` int(11) NOT NULL,
  `amount` float NOT NULL,
  `dest` text NOT NULL,
  `processed` int(11) NOT NULL,
  `info` text NOT NULL,
  `created_at` datetime NOT NULL,
  `processed_at` datetime NOT NULL,
  PRIMARY KEY (`withdrawal_id`),
  KEY `user_serial` (`user_serial`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2010-09-04 20:01:03
