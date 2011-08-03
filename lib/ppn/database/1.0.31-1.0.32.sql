UPDATE server SET version = '1.0.32';

DROP TABLE IF EXISTS messages;

CREATE TABLE messages (
  serial INT UNSIGNED NOT NULL AUTO_INCREMENT,
  send_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  message TEXT DEFAULT '',
  sent CHAR DEFAULT 'n',

  PRIMARY KEY (serial, send_date, sent)
)  ENGINE=InnoDB CHARSET=utf8;
