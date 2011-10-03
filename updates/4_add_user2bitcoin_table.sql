CREATE TABLE `user2bitcoin` (
  `serial` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `user_serial` BIGINT UNSIGNED NOT NULL,
  `currency_serial` BIGINT UNSIGNED NOT NULL,
  `balance` DECIMAL(52,8) UNSIGNED NOT NULL,
  PRIMARY KEY (`serial`),
  INDEX `user_index`(`user_serial`),
  INDEX `currency_index`(`currency_serial`)
)
ENGINE = InnoDB;
)