--
-- Money units are now cents
--
ALTER TABLE `users` CHANGE `play_money` `play_money` INT( 11 ) NULL DEFAULT '100000000';
update users set play_money = play_money * 100;
update tourneys_schedule set buy_in = buy_in * 100, rake = rake * 100;
--
-- Sessions and session history are recorded
--
drop table if exists session;

create table session (
  user_serial int not null,
  started int default 0,
  ended int default 0,
  ip varchar(16),

  primary key (user_serial, ip)
);

drop table if exists session_history;

create table session_history (
  user_serial int not null,
  started int default 0,
  ended int default 0,
  ip varchar(16),

  key session_history_serial (user_serial)
);

drop table if exists users_wins;
--
-- Define functions by which a given set of money is created
--
alter table server add play_money_generator varchar(64) default "periodic";
alter table users add play_money_rebuy int default 0;
alter table server add custom_money_generator varchar(64) default "";
