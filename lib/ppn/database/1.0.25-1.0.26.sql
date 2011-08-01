-- each player may be associated to an affiliate record
ALTER TABLE `users` ADD COLUMN `affiliate` int unsigned default 0;
--
-- Affiliate description
--
create table affiliates (
  serial int unsigned not null auto_increment,
  modified TIMESTAMP,
  created int unsigned not null,

  users_count int unsigned default 0,
  users_rake int unsigned default 0,
  users_points int unsigned default 0,

  --
  -- percentage of the rake assigned to the affiliate
  --
  share int unsigned default 0, 

  companyname varchar(255) default "",
  firstname varchar(255) default "",
  lastname varchar(255) default "",
  addr_street varchar(255) default "",
  addr_street2 varchar(255) default "",
  addr_zip varchar(64) default "",
  addr_town varchar(64) default "",
  addr_state varchar(128) default "",
  addr_country varchar(64) default "",
  phone varchar(64) default "",

  url TEXT,
  notes TEXT,

  primary key (serial)
);
