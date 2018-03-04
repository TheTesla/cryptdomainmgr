

-- CREATE USER IF NOT EXISTS `{{ mailserver_db_user_name }}`@`{{ dbhost }}`;

-- SET PASSWORD FOR `{{ mailserver_db_user_name }}`@`{{ dbhost }}` = PASSWORD(`{{ mailserver_db_user_passwd }}`);

CREATE DATABASE IF NOT EXISTS `dovecot`;

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

--
-- Current Database: `postfix`
--

CREATE DATABASE IF NOT EXISTS `postfix`;

USE `postfix`;


--
-- Table structure for table `smtp_users`
--

CREATE TABLE IF NOT EXISTS `smtp_users` (
  `userid` varchar(40) NOT NULL,
  `client_idnr` varchar(40) NOT NULL,
  `username` varchar(80) NOT NULL,
  `passwd` varchar(256) NOT NULL,
  `email` varchar(80) DEFAULT NULL,
  `forward_only` tinyint(1) NOT NULL DEFAULT '0',
  PRIMARY KEY (`userid`,`client_idnr`),
  UNIQUE KEY `username` (`username`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


--
-- Table structure for table `smtp_destinations`
--

CREATE TABLE IF NOT EXISTS `smtp_destinations` (
  `userid` varchar(40) NOT NULL,
  `source` varchar(80) NOT NULL,
  `destination` varchar(80) NOT NULL,
  KEY `smtp_destinations::userid--smtp_users::userid` (`userid`),
  CONSTRAINT `smtp_destinations::userid--smtp_users::userid` FOREIGN KEY (`userid`) REFERENCES `smtp_users` (`userid`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE IF NOT EXISTS `smtp_extra_properties` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `email` varchar(80) DEFAULT NULL,
  `sendonly` boolean DEFAULT '0',
  PRIMARY KEY (`id`),
  UNIQUE KEY (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE IF NOT EXISTS `tlspolicies` (
    `id` int unsigned NOT NULL AUTO_INCREMENT,
    `domain` varchar(255) NOT NULL,
    `policy` enum('none', 'may', 'encrypt', 'dane', 'dane-only', 'fingerprint', 'verify', 'secure') NOT NULL,
    `params` varchar(255),
    PRIMARY KEY (`id`),
    UNIQUE KEY (`domain`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

GRANT USAGE ON *.* TO '{{ mailserver_db_user_name }}'@'{{ dbhost }}' IDENTIFIED BY '{{ mailserver_db_user_passwd }}';
GRANT ALL PRIVILEGES ON dovecot.* TO '{{ mailserver_db_user_name }}'@'{{ dbhost }}';
GRANT ALL PRIVILEGES ON postfix.* TO '{{ mailserver_db_user_name }}'@'{{ dbhost }}';


--
-- database for spamfilter
--

CREATE DATABASE IF NOT EXISTS `spamassassin`;

GRANT ALL ON spamassassin.* TO 'spamassassin'@'{{ dbhost }}' IDENTIFIED BY '{{ spamass_passwd }}';



