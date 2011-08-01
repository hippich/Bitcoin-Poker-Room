ALTER TABLE `hands` ADD `created` TIMESTAMP NOT NULL ;
ALTER TABLE `hands` ADD INDEX ( `created` ) ; 
