ALTER TABLE `pythonpokernetwork`.`user2money` MODIFY COLUMN `points` DECIMAL(64,4)  NOT NULL DEFAULT 0;
ALTER TABLE `pythonpokernetwork`.`user2money` ADD COLUMN `points_cashed` DECIMAL(64,4)  NOT NULL DEFAULT 0 AFTER `points`;


