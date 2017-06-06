
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


