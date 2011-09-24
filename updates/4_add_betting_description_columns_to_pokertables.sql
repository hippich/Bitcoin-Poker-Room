ALTER TABLE `pokertables` ADD COLUMN `small_blind` BIGINT UNSIGNED NOT NULL AFTER `betting_structure`,
 ADD COLUMN `big_blind` BIGINT UNSIGNED NOT NULL AFTER `small_blind`,
 ADD COLUMN `ante_value` BIGINT UNSIGNED NOT NULL AFTER `big_blind`,
 ADD COLUMN `ante_bring_in` BIGINT UNSIGNED NOT NULL AFTER `ante_value`,
 ADD COLUMN `limit_type` varchar(20)  NOT NULL AFTER `ante_bring_in`,
 ADD COLUMN `betting_description` VARCHAR(255)  NOT NULL AFTER `big_blind`;

ALTER TABLE `pokertables` ADD INDEX `small_blind`(`small_blind`),
 ADD INDEX `big_blind`(`big_blind`),
 ADD INDEX `limit`(`limit_type`);

