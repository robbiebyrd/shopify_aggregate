CREATE TABLE IF NOT EXISTS `user` (
	id INT(11) NOT NULL auto_increment,
	email varchar(255) not null,
	password varchar(255) not null,
	is_active tinyint(1) not null default '0',
	first_name varchar(100) not null default '',
	last_name varchar(100) not null default '',
	UNIQUE `email` (`email`),
	PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;

CREATE TABLE IF NOT EXISTS `audit_status` (
	id INT(11) NOT NULL auto_increment,
	shop_id INT(11) NOT NULL,
	status VARCHAR(100) NOT NULL,
	logged_on datetime NOT NULL,
	PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;
