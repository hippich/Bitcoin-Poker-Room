ALTER TABLE `hands` ENGINE=InnoDB DEFAULT CHARSET=utf8; # was ENGINE=MyISAM DEFAULT CHARSET=latin1
ALTER TABLE `pokertables` DROP COLUMN `custom_money`; # was char(1) default 'n'
ALTER TABLE `pokertables` ADD COLUMN `currency_serial` int(11) NOT NULL;
ALTER TABLE `pokertables` ENGINE=InnoDB DEFAULT CHARSET=utf8; # was ENGINE=MyISAM DEFAULT CHARSET=latin1
ALTER TABLE `server` DROP COLUMN `custom_money_generator`; # was varchar(64) default ''
ALTER TABLE `server` DROP COLUMN `play_money_generator`; # was varchar(64) default 'periodic(''daily'', 10000000)'
ALTER TABLE `server` ENGINE=InnoDB DEFAULT CHARSET=utf8; # was ENGINE=MyISAM DEFAULT CHARSET=latin1
ALTER TABLE `session` ENGINE=InnoDB DEFAULT CHARSET=utf8; # was ENGINE=MyISAM DEFAULT CHARSET=latin1
ALTER TABLE `session_history` ENGINE=InnoDB DEFAULT CHARSET=utf8; # was ENGINE=MyISAM DEFAULT CHARSET=latin1
ALTER TABLE `tourneys` DROP COLUMN `custom_money`; # was char(1) default 'n'
ALTER TABLE `tourneys` ADD COLUMN `currency_serial` int(11) default NULL;
ALTER TABLE `tourneys` ENGINE=InnoDB DEFAULT CHARSET=utf8; # was ENGINE=MyISAM DEFAULT CHARSET=latin1
ALTER TABLE `tourneys_schedule` DROP COLUMN `custom_money`; # was char(1) default 'n'
ALTER TABLE `tourneys_schedule` ADD COLUMN `currency_serial` int(11) default NULL;
ALTER TABLE `tourneys_schedule` ENGINE=InnoDB DEFAULT CHARSET=utf8; # was ENGINE=MyISAM DEFAULT CHARSET=latin1
ALTER TABLE `user2hand` ENGINE=InnoDB DEFAULT CHARSET=utf8; # was ENGINE=MyISAM DEFAULT CHARSET=latin1
ALTER TABLE `user2table` DROP COLUMN `custom_money`; # was char(1) default 'n'
ALTER TABLE `user2table` ENGINE=InnoDB DEFAULT CHARSET=utf8; # was ENGINE=MyISAM DEFAULT CHARSET=latin1
ALTER TABLE `user2tourney` ENGINE=InnoDB DEFAULT CHARSET=utf8; # was ENGINE=MyISAM DEFAULT CHARSET=latin1
ALTER TABLE `users` DROP COLUMN `point_money`; # was int(11) default '5000'
ALTER TABLE `users` DROP COLUMN `custom_money`; # was int(11) default '0'
ALTER TABLE `users` DROP COLUMN `play_money_rebuy`; # was int(11) default '0'
ALTER TABLE `users` DROP COLUMN `play_money`; # was int(11) default '100000000'
ALTER TABLE `users` ENGINE=InnoDB DEFAULT CHARSET=utf8; # was ENGINE=MyISAM DEFAULT CHARSET=latin1
ALTER TABLE `users_private` ENGINE=InnoDB DEFAULT CHARSET=utf8; # was ENGINE=MyISAM DEFAULT CHARSET=latin1
ALTER TABLE `users_private` ADD COLUMN `firstname` varchar(255) default "";
ALTER TABLE `users_private` ADD COLUMN `lastname` varchar(255) default "";
ALTER TABLE `users_private` ADD COLUMN `addr_street2` varchar(255) default "";
ALTER TABLE `users_transactions` DROP COLUMN `status_time`; # was int(11) default '0'
ALTER TABLE `users_transactions` DROP COLUMN `custom_money`; # was char(1) default 'n'
ALTER TABLE `users_transactions` DROP COLUMN `created`; # was int(11) default '0'
ALTER TABLE `users_transactions` ADD COLUMN `modified` timestamp NOT NULL default CURRENT_TIMESTAMP on update CURRENT_TIMESTAMP;
ALTER TABLE `users_transactions` ADD COLUMN `currency_serial` int(11) NOT NULL;
CREATE TABLE `counter` (
  `transaction_id` char(40) NOT NULL,
  `user_serial` int(11) NOT NULL,
  `currency_serial` int(11) NOT NULL,
  `serial` int(11) NOT NULL,
  `name` char(40) NOT NULL,
  `value` int(11) NOT NULL,
  `status` char(1) NOT NULL default 'y',
  PRIMARY KEY  (`currency_serial`,`name`,`serial`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `currencies` (
  `serial` int(11) NOT NULL auto_increment,
  `url` char(255) NOT NULL,
  `symbol` char(8) default NULL,
  `name` char(32) default NULL,
  `cash_out` int(11) default NULL,
  PRIMARY KEY  (`serial`,`url`),
  UNIQUE KEY `url` (`url`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


CREATE TABLE `safe` (
  `currency_serial` int(11) NOT NULL,
  `serial` int(11) NOT NULL,
  `name` char(40) NOT NULL,
  `value` int(11) NOT NULL,
  PRIMARY KEY  (`currency_serial`,`serial`,`value`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `user2money` (
  `user_serial` int(10) unsigned NOT NULL,
  `currency_serial` int(10) unsigned NOT NULL,
  `amount` int(11) NOT NULL,
  `rake` int(11) NOT NULL default '0',
  `points` int(11) NOT NULL default '0',
  PRIMARY KEY  (`user_serial`,`currency_serial`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

ALTER TABLE `hands` CHANGE COLUMN `name` `name` varchar(32) default NULL; # was varchar(32) character set latin1 default NULL
ALTER TABLE `hands` CHANGE COLUMN `description` `description` text NOT NULL; # was text character set latin1 NOT NULL
ALTER TABLE `pokertables` CHANGE COLUMN `name` `name` varchar(32) default NULL; # was varchar(32) character set latin1 default NULL
ALTER TABLE `server` CHANGE COLUMN `version` `version` varchar(16) NOT NULL; # was varchar(16) character set latin1 NOT NULL
ALTER TABLE `session` CHANGE COLUMN `ip` `ip` varchar(16) NOT NULL default ''; # was varchar(16) character set latin1 NOT NULL default ''
ALTER TABLE `session_history` CHANGE COLUMN `ip` `ip` varchar(16) default NULL; # was varchar(16) character set latin1 default NULL
ALTER TABLE `tourneys` CHANGE COLUMN `description_short` `description_short` varchar(64) default NULL; # was varchar(64) character set latin1 default NULL
ALTER TABLE `tourneys` CHANGE COLUMN `description_long` `description_long` text; # was text character set latin1
ALTER TABLE `tourneys` CHANGE COLUMN `variant` `variant` varchar(32) default NULL; # was varchar(32) character set latin1 default NULL
ALTER TABLE `tourneys` CHANGE COLUMN `state` `state` varchar(32) default 'registering'; # was varchar(32) character set latin1 default 'registering'
ALTER TABLE `tourneys` CHANGE COLUMN `sit_n_go` `sit_n_go` char(1) default 'y'; # was char(1) character set latin1 default 'y'
ALTER TABLE `tourneys` CHANGE COLUMN `betting_structure` `betting_structure` varchar(32) default NULL; # was varchar(32) character set latin1 default NULL
ALTER TABLE `tourneys` CHANGE COLUMN `name` `name` varchar(32) default NULL; # was varchar(32) character set latin1 default NULL
ALTER TABLE `tourneys_schedule` CHANGE COLUMN `description_short` `description_short` varchar(64) default NULL; # was varchar(64) character set latin1 default NULL
ALTER TABLE `tourneys_schedule` CHANGE COLUMN `description_long` `description_long` text; # was text character set latin1
ALTER TABLE `tourneys_schedule` CHANGE COLUMN `variant` `variant` varchar(32) default NULL; # was varchar(32) character set latin1 default NULL
ALTER TABLE `tourneys_schedule` CHANGE COLUMN `respawn` `respawn` char(1) default 'n'; # was char(1) character set latin1 default 'n'
ALTER TABLE `tourneys_schedule` CHANGE COLUMN `sit_n_go` `sit_n_go` char(1) default 'y'; # was char(1) character set latin1 default 'y'
ALTER TABLE `tourneys_schedule` CHANGE COLUMN `betting_structure` `betting_structure` varchar(32) default NULL; # was varchar(32) character set latin1 default NULL
ALTER TABLE `tourneys_schedule` CHANGE COLUMN `name` `name` varchar(32) default NULL; # was varchar(32) character set latin1 default NULL
ALTER TABLE `users` CHANGE COLUMN `skin_url` `skin_url` varchar(32) default 'random'; # was varchar(32) character set latin1 default 'random'
ALTER TABLE `users` CHANGE COLUMN `skin_outfit` `skin_outfit` text; # was text character set latin1
ALTER TABLE `users` CHANGE COLUMN `password` `password` varchar(32) default NULL; # was varchar(32) character set latin1 default NULL
ALTER TABLE `users` CHANGE COLUMN `skin_image_type` `skin_image_type` varchar(32) default NULL; # was varchar(32) character set latin1 default NULL
ALTER TABLE `users` CHANGE COLUMN `name` `name` varchar(32) default NULL; # was varchar(32) character set latin1 default NULL
ALTER TABLE `users` CHANGE COLUMN `email` `email` varchar(128) default NULL; # was varchar(128) character set latin1 default NULL
ALTER TABLE `users_private` CHANGE COLUMN `addr_street` `addr_street` varchar(255) default ''; # was varchar(255) character set latin1 default ''
ALTER TABLE `users_private` CHANGE COLUMN `addr_state` `addr_state` varchar(128) default ''; # was varchar(128) character set latin1 default ''
ALTER TABLE `users_private` CHANGE COLUMN `verified` `verified` char(1) default 'n'; # was char(1) character set latin1 default 'n'
ALTER TABLE `users_private` CHANGE COLUMN `addr_country` `addr_country` varchar(64) default ''; # was varchar(64) character set latin1 default ''
ALTER TABLE `users_private` CHANGE COLUMN `phone` `phone` varchar(64) default ''; # was varchar(64) character set latin1 default ''
ALTER TABLE `users_private` CHANGE COLUMN `addr_zip` `addr_zip` varchar(64) default ''; # was varchar(64) character set latin1 default ''
ALTER TABLE `users_private` CHANGE COLUMN `addr_town` `addr_town` varchar(64) default ''; # was varchar(64) character set latin1 default ''
