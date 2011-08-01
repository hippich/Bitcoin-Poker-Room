--
-- Self-sufficient primary key for browsing session history
--
ALTER TABLE `session_history` ADD PRIMARY KEY ( `user_serial` , `started` , `ended` ) ;
