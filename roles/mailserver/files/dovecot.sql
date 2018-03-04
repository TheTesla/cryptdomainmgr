
USE `dovecot`;

--
-- Table structure for table `dovecot_users`
--

CREATE TABLE IF NOT EXISTS `dovecot_users` (
  `userid` varchar(40) NOT NULL,
  `domain` varchar(80) NOT NULL DEFAULT '',
  `username` varchar(80) NOT NULL,
  `password` varchar(256) NOT NULL,
  `quota_bytes` bigint(20) NOT NULL DEFAULT '0',
  `quota_message` int(11) NOT NULL DEFAULT '0',
  `uid` varchar(20) DEFAULT NULL,
  `gid` varchar(20) DEFAULT NULL,
  `home` varchar(256) DEFAULT NULL,
  `last_login` datetime DEFAULT NULL,
  PRIMARY KEY (`userid`,`domain`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Table structure for table `dovecot_usage`
--

CREATE TABLE IF NOT EXISTS `dovecot_usage` (
  `username` varchar(80) NOT NULL,
  `storage` bigint(20) NOT NULL DEFAULT '0',
  `messages` bigint(20) NOT NULL DEFAULT '0',
  PRIMARY KEY (`username`),
  CONSTRAINT `dovecot_usage::username--dovecot_users::username` FOREIGN KEY (`username`) REFERENCES `dovecot_users` (`username`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


